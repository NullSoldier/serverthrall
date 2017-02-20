import time
import logging


class Thrall(object):

    def __init__(self, steamcmd, config, plugins, server):
        self.steamcmd = steamcmd
        self.config = config
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
        print 'Tearing down daemon'
        self.config.save()
        self.server.close()

    def start(self):
        if not self.server.is_running():
            self.server.start()

        for plugin in self.plugins:
            if plugin.enabled:
                plugin.ready(self.server, self.steamcmd, self)

        while True:
            for plugin in self.plugins:
                if not plugin.enabled:
                    continue

                try:
                    plugin.tick()
                except Exception:
                    self.logger.exception('Unloading %s plugin after error ' % plugin.name)
                    self.plugins.remove(plugin)

            self.config.save()
            time.sleep(5)
