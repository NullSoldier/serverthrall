from .thrallplugin import ThrallPlugin
from datetime import datetime
import time


class UptimeTracker(ThrallPlugin):

    def __init__(self, config):
        super(UptimeTracker, self).__init__(config)
        self.config.set_default('initial', self.get_current_timestamp())
        self.config.set_default('seconds_up', 0)
        self.config.queue_save()
        self.last_check = None

    def ready(self, steamcmd, server, thrall):
        super(UptimeTracker, self).ready(steamcmd, server, thrall)
        self.initial = self.config.getfloat('initial')
        self.seconds_up = self.config.getfloat('seconds_up')

    def get_current_timestamp(self):
        return time.mktime(datetime.now().timetuple())

    def get_total_lifespan(self):
        return self.get_current_timestamp() - self.initial

    def get_uptime(self):
        total_lifespan_seconds = self.get_total_lifespan()
        if total_lifespan_seconds == 0:
            return 0
        return (self.seconds_up / total_lifespan_seconds) * 100

    def tick(self):
        if self.server.is_running():
            if self.last_check is None:
                self.last_check = self.get_current_timestamp()

            current = self.get_current_timestamp()
            elapsed = current - self.last_check
            self.seconds_up += elapsed
            self.last_check = current
            self.config.set('seconds_up', self.seconds_up)
            self.config.queue_save()

            self.logger.info(
                'Uptime at %s percent (%s / %s)' % (
                round(self.get_uptime(), 2),
                self.seconds_up,
                self.get_total_lifespan()))
