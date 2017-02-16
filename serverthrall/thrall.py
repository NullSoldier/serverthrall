import time


class Thrall(object):

    def __init__(self, steamcmd, config, plugins, server):
        self.steamcmd = steamcmd
        self.config = config
        self.plugins = plugins
        self.server = server

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
        self.close_server()

    def start(self):
        print 'started thrall', self.server.is_running(), self.server.process
        if not self.server.is_running():
            self.server.start()

        for plugin in self.plugins:
            plugin.ready(self.server, self.steamcmd)

        while True:
            print 'Tick'
            for plugin in self.plugins:
                plugin.tick()
            self.config.save()
            time.sleep(5)
