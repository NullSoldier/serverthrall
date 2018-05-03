from .discord import Discord
from .intervaltickplugin import IntervalTickPlugin

class DownRecovery(IntervalTickPlugin):

    THIRTY_SECONDS = 30

    def __init__(self, config):
        super(DownRecovery, self).__init__(config)
        config.set_default('interval.interval_seconds', self.THIRTY_SECONDS)
        config.queue_save()

    def ready(self, steamcmd, server, thrall):
        super(DownRecovery, self).ready(steamcmd, server, thrall)
        self.discord = thrall.get_plugin(Discord)

    def tick_interval(self):
        if self.server.is_running():
            return

        if self.discord is not None:
            self.discord.send_message('DownRecovery', "The server may have crashed, starting it back up.")

        self.logger.error('Server down, bringing it back online')
        self.server.close()
        self.server.start()
