import logging


class ThrallPlugin(object):

    def __init__(self, config, data):
        self.config = config
        self.data = data
        self.name = self.__class__.__name__
        self.config.set_default('enabled', 'true')
        self.config.queue_save()
        self.enabled = self.config.getboolean('enabled')

    def ready(self, server, steamcmd, thrall):
        self.server = server
        self.steamcmd = steamcmd
        self.thrall = thrall
        self.logger = logging.getLogger('serverthrall.' + self.name)
        self.configure_logging();

    def unload(self):
        self.enabled = False

    def configure_logging(self):
        self.logger.setLevel(logging.INFO)

        if self.config.has_option('log_level'):
            configured = self.config.get('log_level').lower()

            self.logger.setLevel({
                'debug': logging.DEBUG,
                'info': logging.INFO,
                'warning': logging.WARNING,
                'error': logging.ERROR,
                'critical': logging.CRITICAL,
            }.get(configured, logging.INFO))
