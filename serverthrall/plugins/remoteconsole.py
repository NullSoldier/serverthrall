from ..conanconfig import CONAN_SETTINGS_MAPPING
from .intervaltickplugin import IntervalTickPlugin
from valve.rcon import RCON, RCONError


class RemoteConsole(IntervalTickPlugin):

    ONE_MINUTE = 60
    TWO_MINUTES = 2 * 60

    def __init__(self, config):
        config.set_default('enabled', 'false')
        super(RemoteConsole, self).__init__(config)
        config.set_default('interval.interval_seconds', self.ONE_MINUTE)
        config.queue_save()

    def execute_safe(self, command):
        if not self.enabled:
            return

        rcon_host     = self.server.multihome
        rcon_port     = self.thrall.conan_config.get(*CONAN_SETTINGS_MAPPING['RconPort'])
        rcon_password = self.thrall.conan_config.get(*CONAN_SETTINGS_MAPPING['RconPassword'])

        if not rcon_host or not rcon_port or not rcon_password:
            return

        self.logger.debug('Executing: ' + command)

        try:
            with RCON((rcon_host, int(rcon_port)), rcon_password) as rcon:
                return rcon.execute(command)
        except RCONError:
            self.logger.error('Error sending command ' + command)
        except Exception:
            self.logger.exception('Error when exceuting RCON command')

    def broadcast(self, message):
        return self.execute_safe('broadcast "%s"' % message)

    def tick_interval(self):
        pass
