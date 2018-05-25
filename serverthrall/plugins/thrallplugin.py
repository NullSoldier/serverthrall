import logging


class ThrallPlugin(object):

    DEFAULT_LOGGING = logging.INFO

    def __init__(self, config):
        self.config = config
        self.name = self.__class__.__name__
        self.config.set_default('enabled', 'true')
        self.config.queue_save()
        self.enabled = self.config.getboolean('enabled')

    def ready(self, server, steamcmd, thrall):
        self.server = server
        self.steamcmd = steamcmd
        self.thrall = thrall
        self.logger = logging.getLogger('serverthrall.' + self.name)
        self.logger.setLevel(self.DEFAULT_LOGGING)

        if self.config.has_option('log_level'):
            self.logger.setLevel({
                'debug': logging.DEBUG,
                'info': logging.INFO,
                'warning': logging.WARNING,
                'error': logging.ERROR,
                'critical': logging.CRITICAL,
            }.get(self.config.get('log_level').lower(), self.DEFAULT_LOGGING))

    def unload(self):
        self.enabled = False
