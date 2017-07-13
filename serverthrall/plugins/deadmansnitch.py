from .intervaltickplugin import IntervalTickPlugin
import requests


class DeadManSnitch(IntervalTickPlugin):

    TEN_MINUTES = 10 * 60

    def __init__(self, config):
        super(DeadManSnitch, self).__init__(config)
        config.set_default('interval.interval_seconds', self.TEN_MINUTES)
        config.set_default('snitch_url', '')
        config.queue_save()

    def ready(self, *args, **kwargs):
        super(DeadManSnitch, self).ready(*args, **kwargs)
        self.snitch_url = self.config.get('snitch_url')
        self.tick_early()

    def tick_interval(self):
        if self.snitch_url and self.server.is_running():
            self.logger.debug('Snitching to %s' % self.snitch_url)
            try:
                requests.get(self.snitch_url)
            except:
                pass
