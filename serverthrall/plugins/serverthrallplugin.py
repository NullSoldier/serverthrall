import logging


class ServerThrallPlugin(object):

    def __init__(self, config):
        self.config = config

    def ready(self, server, steamcmd):
        self.server = server
        self.steamcmd = steamcmd
        self.logger = logging.getLogger('serverthrall.' + self.__class__.__name__)
