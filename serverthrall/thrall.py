import time
import logging


class Thrall(object):

    def __init__(self, steamcmd, config, conan_config, plugins, server):
        self.steamcmd = steamcmd
        self.config = config
        self.conan_config = conan_config
        self.plugins = plugins
        self.server = server
        self.logger = logging.getLogger('serverthrall')

    def validate(self):
        # load configuration
        # validate configuration
            # check if config exists
            # check if game is installed
            # check if steam cmd is located
        # look for existing server
            # create instance of ConanServer
            # attach to running process
        # start thrall with ConanServer thrall.run(server)
        pass

    def stop(self):
        self.logger.info('Stopping ServerThrall')
        self.config.save()

    def start(self):
        if not self.server.is_running():
            self.server.start()
            self.conan_config.refresh()

        for plugin in self.plugins:
            if plugin.enabled:
                try:
                    plugin.ready(self.server, self.steamcmd, self)
                except Exception:
                    self.logger.exception('Unloading %s plugin after error ' % plugin.name)
                    self.plugins.remove(plugin)

        while True:
            for plugin in self.plugins:
                if not plugin.enabled:
                    continue

                try:
                    plugin.tick()
                except Exception:
                    self.logger.exception('Unloading %s plugin after error ' % plugin.name)
                    self.plugins.remove(plugin)

            self.config.save_if_queued()
            time.sleep(5)
