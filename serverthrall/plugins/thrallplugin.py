import logging


class ThrallPlugin(object):

    def __init__(self, config):
        self.config = config
        self.name = self.__class__.__name__
        self.enabled = None
        self.config.set_default('enabled', 'true')

    def ready(self, server, steamcmd, thrall):
        self.server = server
        self.steamcmd = steamcmd
        self.thrall = thrall
        self.logger = logging.getLogger('serverthrall.' + self.name)
        self.enabled = self.config.getboolean('enabled')
