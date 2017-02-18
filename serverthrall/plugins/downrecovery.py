from .serverthrallplugin import ServerThrallPlugin


class DownRecovery(ServerThrallPlugin):

    def tick(self):
        if not self.server.is_running():
            print('Server currently down. Rebooting')
            # self.logger.info('Server down... rebooting')
            self.server.close()
            self.server.start()
