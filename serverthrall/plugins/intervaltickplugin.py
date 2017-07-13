from .intervaltrigger import IntervalTrigger
from .thrallplugin import ThrallPlugin


class IntervalTickPlugin(ThrallPlugin):

    ONE_MINUTE_IN_SECONDS = 60

    def __init__(self, config):
        super(IntervalTickPlugin, self).__init__(config)
        self.config.set_default('interval.last_checked_seconds', 0)
        self.config.set_default('interval.interval_seconds', self.ONE_MINUTE_IN_SECONDS)
        self.config.queue_save()
        self.back_off_seconds = 0
        self.back_off_multiplier = 0.5
        self.back_off_called = False

    def ready(self, steamcmd, server, thrall):
        super(IntervalTickPlugin, self).ready(steamcmd, server, thrall)

        self.trigger = IntervalTrigger(
            self.config.getfloat('interval.last_checked_seconds'),
            self.config.getfloat('interval.interval_seconds'))

    def tick_early(self):
        self.trigger.trigger()

    def back_off(self):
        self.back_off_seconds = (
            self.config.getint('interval.interval_seconds') * self.back_off_multiplier)
        self.back_off_multiplier += 2
        self.back_off_called = True

    def tick(self):
        if self.trigger.is_ready(self.back_off_seconds):
            self.config.set('interval.last_checked_seconds', self.trigger.last_checked)
            self.config.queue_save()
            self.trigger.reset()
            self.tick_interval()

            if not self.back_off_called:
                self.back_off_seconds = 0
                self.back_off_multiplier = 0.5

            self.back_off_called = False

    def tick_interval(self):
        raise Exception('Must override tick_interval')
