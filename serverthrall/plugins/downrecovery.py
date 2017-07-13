from .intervaltickplugin import IntervalTickPlugin

class DownRecovery(IntervalTickPlugin):

    THIRTY_SECONDS = 30

    def __init__(self, config):
        super(DownRecovery, self).__init__(config)
        config.set_default('interval.interval_seconds', self.THIRTY_SECONDS)
        config.queue_save()

    def tick_interval(self):
        if not self.server.is_running():
            self.logger.error('Server down, bringing it back online')
            self.server.close()
            self.server.start()
