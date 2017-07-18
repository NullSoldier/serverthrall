from .intervaltickplugin import IntervalTickPlugin
from contextlib import contextmanager
from serverthrall.exceptions import UnloadPluginException
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
        self.snitch_url = self.config.get('snitch_url').strip()
        self.tick_early()

        if not self.snitch_url:
            self.logger.warn('No snitch url specified, unloading plugin until you fix your configuration')
            raise UnloadPluginException()

    @contextmanager
    def ignore_all_errors(self):
        try:
            yield
        except:
            pass

    def tick_interval(self):
        if self.server.is_running():
            self.logger.debug('Snitching to %s' % self.snitch_url)
            with self.ignore_all_errors():
                requests.get(self.snitch_url)
