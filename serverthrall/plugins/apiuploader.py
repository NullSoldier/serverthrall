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
    SERVER_THRALL_API_URL = 'http://192.168.1.145:8000/'

    def __init__(self, config):
        config.set_default('interval.interval_seconds', 60)
        config.set_default('private_secret', self.NO_SECRET)
        config.set_default('server_id', '')
        config.set_default('last_sync_time', '')
        super(ApiUploader, self).__init__(config)

    def ready(self, steamcmd, server, thrall):
        super(ApiUploader, self).ready(steamcmd, server, thrall)
        self.server_id = self.config.get('server_id')
        self.private_secret = self.config.get('private_secret')

        db_path = os.path.join(self.thrall.config.get('conan_server_directory'),
            'ConanSandbox\\Saved\\game.db')

        if not os.path.exists(db_path):
            raise Exception('Server DB not found at path %s' % db_path)

        self.client = ConanDbClient(db_path)
        # TODO: Load Group UID from Config and gracefully ignore, if UID is not set in the config
        self.ginfo_group_uid = '-Knj7Mt-7frt_Wtpvq_9'

        self.logger.info('Connecting to Database '+ self.DB_PATH)

        self.client = ConanDbClient(self.DB_PATH)

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
            requests.post(
                url=(self.SERVER_THRALL_API_URL + '/api/%s/sync/characters') % self.server_id,
                params={'private_secret': self.private_secret, 'ginfo_group_uid': self.ginfo_group_uid},
                json={'characters': characters})
        except ConnectionError:
            self.logger.error('Cant sync server to serverthrallapi')
            self.back_off()
            return