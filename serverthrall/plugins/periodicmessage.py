from .intervaltickplugin import IntervalTickPlugin
from .remoteconsole import RemoteConsole


class PeriodicMessage(IntervalTickPlugin):

    SIX_HOURS = 6 * 60 * 60

    def __init__(self, config):
        config.set_default('enabled', 'false')
        super(PeriodicMessage, self).__init__(config)
        config.set_default('interval.interval_seconds', 10)
        config.queue_save()

    def ready(self, steamcmd, server, thrall):
        super(PeriodicMessage, self).ready(steamcmd, server, thrall)
        self.rcon = thrall.get_plugin(RemoteConsole)

    def tick_interval(self):
        message = self.config.get('message', default=None)

        if not message:
            self.logger.warning('You have not specified a message to broadcast into the server.')
            return

        self.rcon.broadcast(message)
