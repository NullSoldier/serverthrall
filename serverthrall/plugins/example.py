from .intervaltickplugin import IntervalTickPlugin

class ExamplePlugin(IntervalTickPlugin):

    def __init__(self, config):
        super(IntervalTickPlugin, self).__init__(config)
        config.set_default('interval.interval_seconds', 5)
        config.queue_save()

    def ready(self, *args, **kwargs):
        super(ExamplePlugin, self).ready(*args, **kwargs)
        self.logger.info('Example plugin loaded and ready')

    def tick_interval(self):
        self.logger.info('Hello World')
