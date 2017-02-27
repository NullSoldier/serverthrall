from .thrallplugin import ThrallPlugin
from .intervaltrigger import IntervalTrigger


class IntervalTickPlugin(ThrallPlugin):

    ONE_MINUTE_IN_SECONDS = 60

    def __init__(self, config):
        super(IntervalTickPlugin, self).__init__(config)
        self.config.set_default('interval.last_checked_seconds', 0)
        self.config.set_default('interval.interval_seconds', self.ONE_MINUTE_IN_SECONDS)

    def ready(self, steamcmd, server, thrall):
        super(IntervalTickPlugin, self).ready(steamcmd, server, thrall)

        self.trigger = IntervalTrigger(
            self.config.getfloat('interval.last_checked_seconds'),
            self.config.getfloat('interval.interval_seconds'))

    def tick(self):
        if self.trigger.is_ready():
            self.config.set('interval.last_checked_seconds', self.trigger.last_checked)
            self.trigger.reset()
            self.tick_interval()

    def tick_interval(self):
        raise Exception('Must override tick_interval')
