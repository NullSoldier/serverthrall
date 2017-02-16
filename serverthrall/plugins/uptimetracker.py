from .serverthrallplugin import ServerThrallPlugin
from datetime import datetime
import time


class UptimeTracker(ServerThrallPlugin):

    def __init__(self, config):
        super(UptimeTracker, self).__init__(config)
        self.config.set_default('initial', self.get_current_timestamp())
        self.config.set_default('seconds_up', 0)
        self.last_check = None

    def ready(self, steamcmd, server):
        super(UptimeTracker, self).ready(steamcmd, server)
        self.initial = self.config.getfloat('initial')
        self.seconds_up = self.config.getfloat('seconds_up')

    def get_current_timestamp(self):
        return time.mktime(datetime.now().timetuple())

    def get_uptime(self):
        total_seconds = self.get_current_timestamp() - self.initial
        uptime_seconds = self.seconds_up
        return (uptime_seconds / total_seconds) * 100

    def tick(self):
        if self.server.is_running():
            if self.last_check is None:
                self.last_check = self.get_current_timestamp()

            current = self.get_current_timestamp()
            elapsed = current - self.last_check
            self.seconds_up += elapsed
            self.last_check = current
            print 'Uptime at %s percent' % round(self.get_uptime(), 2)
            # self.logger.debug('Uptime at %s%' % self.get_uptime())
