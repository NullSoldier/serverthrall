import logging


class ServerThrallPlugin(object):

    def __init__(self, config):
        self.config = config
        self.name = self.__class__.__name__

    def ready(self, server, steamcmd):
        self.server = server
        self.steamcmd = steamcmd
        self.logger = logging.getLogger('serverthrall.' + self.name)
