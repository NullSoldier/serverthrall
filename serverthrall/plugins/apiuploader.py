from ..conanconfig import CONAN_SETTINGS_MAPPING
from .intervaltickplugin import IntervalTickPlugin
from requests.exceptions import ConnectionError
from serverthrall.conandb import ConanDbClient
import os
import requests


class ApiUploader(IntervalTickPlugin):

    NO_VALUE = ''
    SERVER_THRALL_API_URL = 'http://serverthrallapi.herokuapp.com'
    # SERVER_THRALL_API_URL = 'http://127.0.0.1:8000'

    def __init__(self, config):
        config.set_default('enabled', 'false')
        super(ApiUploader, self).__init__(config)
        config.set_default('interval.interval_seconds', 60)
        config.set_default('private_secret', self.NO_VALUE)
        config.set_default('server_id', self.NO_VALUE)
        config.set_default('ip_address', self.NO_VALUE)
        config.set_default('last_sync_time', self.NO_VALUE)
        config.set_default('ginfo_group_uid', self.NO_VALUE)
        config.set_default('ginfo_access_token', self.NO_VALUE)
        config.queue_save()

    def ready(self, steamcmd, server, thrall):
        super(ApiUploader, self).ready(steamcmd, server, thrall)
        self.server_id = self.config.get('server_id')
        self.private_secret = self.config.get('private_secret')
        self.ginfo_group_uid = self.config.get('ginfo_group_uid')
        self.ginfo_access_token = self.config.get('ginfo_access_token')

        db_path = os.path.join(self.thrall.config.get_server_root(),
            'ConanSandbox\\Saved\\game.db')

        if not os.path.exists(db_path):
            raise Exception('Server DB not found at path %s' % db_path)

        self.client = ConanDbClient(db_path)

        if not self.config.has_option('ip_address_override'):
            self.update_global_ip()

    def is_registered(self):
        return self.config.get('private_secret') != self.NO_VALUE

    def register(self):
        self.logger.info('Registering server with serverthrallapi.')
        response = requests.post(self.SERVER_THRALL_API_URL + '/api/', json={'name': 'Server Thrall Server'})
        response.raise_for_status()

        data = response.json()

        self.server_id = data['id']
        self.private_secret = data['private_secret']

        self.config.set('server_id', self.server_id)
        self.config.set('private_secret', self.private_secret)
        self.config.queue_save()

        self.logger.info('Registered, server id: %s, private secret: %s' % (self.server_id, self.private_secret))

    def tick_interval(self):
        if not self.is_registered():
            try:
                self.register()
            except ConnectionError:
                self.logger.error('Failed to register with serverthrallapi')
                self.back_off()
                return

        payload = self.get_sync_payload()
        url = '%s/api/%s/sync/characters' % (self.SERVER_THRALL_API_URL, self.server_id)
        params = {'private_secret': self.private_secret}

        if self.ginfo_group_uid != self.NO_VALUE and self.ginfo_access_token != "":
            params['ginfo_group_uid'] = self.ginfo_group_uid
            params['ginfo_access_token'] = self.ginfo_access_token

        try:
            requests.post(url=url, params=params, json=payload)
        except ConnectionError:
            self.logger.error('Cant sync server to serverthrallapi')
            self.back_off()
            return

    def update_global_ip(self):
        try:
            response = requests.get('https://api.ipify.org')
        except ConnectionError:
            self.logger.warn('Failed to get global Ip Address of the server.')
            return

        if response.status_code != 200:
            self.logger.warn('Failed to get global Ip Address of the server.')
            return

        self.config.set('ip_address', response.text)

    def get_sync_payload(self):

        def get_setting_or_default(name):
            setting = CONAN_SETTINGS_MAPPING[name]
            value = self.thrall.conan_config.get_setting(setting)
            return value if value is not None else setting.default

        ip_address = self.config.get('ip_address', default=None)
        if self.config.has_option('ip_address_override'):
            ip_address = self.config.get('ip_address_override')

        return {
            'version': self.thrall.config.get('version'),
            'characters': self.client.get_characters(),
            'clans': self.client.get_clans(),
            'server': {
                'name': get_setting_or_default('ServerName'),
                'query_port': get_setting_or_default('QueryPort'),
                'max_players': get_setting_or_default('MaxPlayers'),
                'tick_rate': get_setting_or_default('NetServerMaxTickRate'),
                'ip_address': ip_address,
            }
        }
