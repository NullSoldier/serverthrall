from .serverthrallplugin import ServerThrallPlugin


class DownRecovery(ServerThrallPlugin):

    def tick(self):
        if not self.server.is_running():
            self.logger.error('Server down, bringing it back online')
            self.server.close()
            self.server.start()
