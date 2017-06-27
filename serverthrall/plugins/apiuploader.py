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
    DB_PATH = 'G:\SteamLibrary\steamapps\common\Conan Exiles\ConanSandbox\Saved\game.db'
    SYNC_URL = 'http://serverthrallapi.herokuazzpp.com'
    # SYNC_URL = 'http://localhost:8000'

    def __init__(self, config):
        config.set_default('interval.interval_seconds', 60)
        config.set_default('private_secret', self.NO_SECRET)
        config.set_default('public_secret', self.NO_SECRET)
        config.set_default('server_id', '')
        config.set_default('last_sync_time', '')
        super(ApiUploader, self).__init__(config)

    def ready(self, steamcmd, server, thrall):
        super(ApiUploader, self).ready(steamcmd, server, thrall)
        self.server_id = self.config.get('server_id')
        self.public_secret = self.config.get('public_secret')
        self.private_secret = self.config.get('private_secret')
        self.client = ConanDbClient(self.DB_PATH)

    def is_registered(self):
        return self.config.get('private_secret') != self.NO_SECRET

    def register(self):
        self.logger.info('Registering server with serverthrallapi.')
        response = requests.post(self.SYNC_URL + '/api/', json={'name': 'Server Thrall Server'})
        response.raise_for_status()

        data = response.json()

        self.server_id = data['id']
        self.public_secret = data['public_secret']
        self.private_secret = data['private_secret']

        self.config.set('server_id', self.server_id)
        self.config.set('public_secret', self.public_secret)
        self.config.set('private_secret', self.private_secret)

        self.logger.info('Registered, server id: %s, private secret: %s, public secret: %s' % (self.server_id, self.private_secret, self.public_secret))

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
            response = requests.post(
                url=(self.SYNC_URL + '/api/%s/sync/characters') % self.server_id,
                params={'private_secret': self.private_secret},
                json={'characters': characters})
        except ConnectionError:
            self.logger.error('Cant sync server to serverthrallapi')
            self.back_off()
            return