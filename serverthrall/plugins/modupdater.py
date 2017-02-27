from .thrallplugin import ThrallPlugin
from .intervaltickplugin import IntervalTickPlugin
from serverthrall import settings
from serverthrall import acf
from datetime import datetime
import subprocess
import time
import os


class ModUpdater(IntervalTickPlugin):

    THIRTY_MINUTES_IN_SECONDS = 30 * 60

    def __init__(self, config):
        config.set_default('interval.interval_seconds', THIRTY_MINUTES_IN_SECONDS)
        config.set_default('mod_list', '')
        super(ModUpdater, self).__init__(config)

    def ready(self, steamcmd, server, thrall):
        super(ModUpdater, self).ready(steamcmd, server, thrall)
        self.mod_list = self.config.get('mod_list')

    def update_all_mods(self):
        pass
    
    def tick_interval(self):    
        self.logger.info('Starting to check for mod updates')        
        # mod_manifest_path = os.path.join(self.steamcmd.steamcmd_dir, 'steamapps\\workshop\\appworkshop_%s' % settings.CONAN_CLIENT_APP_ID)
        # mod_path = os.path.join(self.steamcmd.steamcmd_dir, 'steamapps\\workshop\\content\\%s\\%s' % settings.CONAN_CLIENT_APP_ID)
     #    self.steamcmd.update_workshop_item(settings.CONAN_CLIENT_APP_ID, 862785583)

