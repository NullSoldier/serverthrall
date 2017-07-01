from .intervaltickplugin import IntervalTickPlugin
from serverthrall import settings, acf
from datetime import datetime
import time
import subprocess
import os
import sqlite3
import requests
from .intervaltickplugin import IntervalTickPlugin
from serverthrall import settings, acf
from datetime import datetime
import time
import subprocess
import os
import sqlite3
import requests
from serverthrall.conandb import ConanDbClient
from requests.exceptions import ConnectionError


class ApiUploader(IntervalTickPlugin):

    NO_SECRET = ''
    # SERVER_THRALL_API_URL = 'http://serverthrallapi.herokuapp.com'
    SERVER_THRALL_API_URL = 'http://192.168.1.145:8000'

    def __init__(self, config):
        config.set_default('interval.interval_seconds', 5)
        config.set_default('private_secret', self.NO_SECRET)
        config.set_default('server_id', '')
        config.set_default('last_sync_time', '')
        config.set_default('ginfo_group_uid', '')
        config.set_default('ginfo_access_token', '')
        super(ApiUploader, self).__init__(config)

    def ready(self, steamcmd, server, thrall):
        super(ApiUploader, self).ready(steamcmd, server, thrall)
        self.server_id = self.config.get('server_id')
        self.private_secret = self.config.get('private_secret')

        db_path = os.path.join(self.thrall.config.get('conan_server_directory'),
            'ConanSandbox\\Saved\\game.db')

        if not os.path.exists(db_path):
            raise Exception('Server DB not found at path %s' % db_path)

        self.logger.info('Connecting to Database '+ db_path)
        self.client = ConanDbClient(db_path)
        self.ginfo_group_uid = self.config.get('ginfo_group_uid')
        self.ginfo_access_token = self.config.get('ginfo_access_token')


    def is_registered(self):
        return self.config.get('private_secret') != self.NO_SECRET

    def register(self):
        self.logger.info('Registering server with serverthrallapi.')
        response = requests.post(self.SERVER_THRALL_API_URL + '/api/', json={'name': 'Server Thrall Server'})
        response.raise_for_status()

        data = response.json()

        self.server_id = data['id']
        self.private_secret = data['private_secret']

        self.config.set('server_id', self.server_id)
        self.config.set('private_secret', self.private_secret)

        self.logger.info('Registered, server id: %s, private secret: %s' % (self.server_id, self.private_secret))

    def tick_interval(self):
        if not self.is_registered():
            try:
                self.register()
            except ConnectionError:
                self.logger.error('Failed to register with serverthrallapi')
                self.back_off()
                return

        characters = self.client.get_characters()

        try:
            params ={'private_secret': self.private_secret}
            if self.ginfo_group_uid and self.ginfo_group_uid != "" and self.ginfo_access_token and self.ginfo_access_token != "":
                params['ginfo_group_uid'] = self.ginfo_group_uid
                params['ginfo_access_token'] = self.ginfo_access_token
            requests.post(
                url=(self.SERVER_THRALL_API_URL + '/api/%s/sync/characters') % self.server_id,
                params=params,
                json={'characters': characters})
        except ConnectionError:
            self.logger.error('Cant sync server to serverthrallapi')
            self.back_off()
            return