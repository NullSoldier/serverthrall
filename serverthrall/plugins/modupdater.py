from .thrallplugin import ThrallPlugin
from serverthrall import settings
from serverthrall import acf
from datetime import datetime
import subprocess
import time
import os


class ModUpdater(ThrallPlugin):

    def __init__(self, config):
        super(ModUpdater, self).__init__(config)
        self.config.set_default('last_checked_seconds', 0)
        self.config.set_default('check_cooldown_seconds', 5)
        self.config.set_default('installed_mods', '')

    def ready(self, steamcmd, server, thrall):
        super(ModUpdater, self).ready(steamcmd, server, thrall)
        self.last_checked_seconds = self.config.getfloat('last_checked_seconds')
        self.check_cooldown_seconds = self.config.getfloat('check_cooldown_seconds')

    def get_current_timestamp(self):
        return time.mktime(datetime.now().timetuple())

    def update_all_mods(self):
        pass
    
    def tick(self):
        current_time = self.get_current_timestamp()
        seconds_since_last_update = current_time - self.last_checked_seconds

        if seconds_since_last_update >= self.check_cooldown_seconds:
            self.logger.info('Starting to check for mod updates')
            self.last_checked_seconds = current_time
            self.config.set('last_checked_seconds', current_time)

        # mod_manifest_path = os.path.join(self.steamcmd.steamcmd_dir, 'steamapps\\workshop\\appworkshop_%s' % settings.CONAN_CLIENT_APP_ID)
        # mod_path = os.path.join(self.steamcmd.steamcmd_dir, 'steamapps\\workshop\\content\\%s\\%s' % settings.CONAN_CLIENT_APP_ID)
     #    self.steamcmd.update_workshop_item(settings.CONAN_CLIENT_APP_ID, 862785583)

