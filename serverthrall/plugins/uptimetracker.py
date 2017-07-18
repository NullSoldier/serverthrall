from .thrallplugin import ThrallPlugin
from serverthrall.utils import IntervalTrigger
from datetime import datetime
import time


class UptimeTracker(ThrallPlugin):

    SIX_HOURS_IN_SECONDS = 6 * 60 * 60
    TEN_MINUTES_IN_SECONDS = 10 * 60
    FIVE_SECONDS = 5
    FIVE_MINUTES = 5 * 60

    def __init__(self, config):
        super(UptimeTracker, self).__init__(config)
        self.config.set_default('initial', self.get_current_timestamp())
        self.config.set_default('seconds_up', 0)
        self.config.set_default('uptime_percent', 0)
        self.config.queue_save()
        self.last_check = None

        now = self.get_current_timestamp()
        self.delta_trigger = IntervalTrigger(now, self.FIVE_SECONDS)
        self.config_trigger = IntervalTrigger(now, self.FIVE_MINUTES)
        self.report_trigger = IntervalTrigger(now, self.SIX_HOURS_IN_SECONDS)

    def ready(self, steamcmd, server, thrall):
        super(UptimeTracker, self).ready(steamcmd, server, thrall)
        self.initial = self.config.getfloat('initial')
        self.seconds_up = self.config.getfloat('seconds_up')
        self.uptime_percent = self.config.getfloat('uptime_percent')
        self.delta_trigger.trigger()
        self.config_trigger.trigger()
        self.report_trigger.trigger()

    def unload(self):
        self.update_time()
        self.update_config()

    def get_current_timestamp(self):
        return time.mktime(datetime.now().timetuple())

    def get_total_lifespan(self):
        return self.get_current_timestamp() - self.initial

    def get_uptime(self):
        total_lifespan_seconds = self.get_total_lifespan()
        if total_lifespan_seconds == 0:
            return 100
        return (self.seconds_up / total_lifespan_seconds) * 100

    def update_time(self):
        if self.server.is_running():
            current = self.get_current_timestamp()

            if self.last_check is None:
                self.last_check = current

            self.seconds_up += current - self.last_check
            self.last_check = current

    def update_config(self):
        self.uptime_percent = round(self.get_uptime(), 2)
        self.config.set('seconds_up', self.seconds_up)
        self.config.set('uptime_percent', self.uptime_percent)
        self.config.queue_save()

    def tick(self):
        if self.delta_trigger.is_ready():
            self.delta_trigger.reset()
            self.update_time()

            # update the config when the numbers are much smaller
            if self.seconds_up < self.TEN_MINUTES_IN_SECONDS:
                self.config_trigger.trigger()

        if self.config_trigger.is_ready():
            self.config_trigger.reset()
            self.update_config()

        if self.report_trigger.is_ready():
            self.report_trigger.reset()
            self.logger.info('Server Uptime at %s percent' % self.uptime_percent)
