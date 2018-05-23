from ..conanconfig import CONAN_SETTINGS_MAPPING
from .intervaltickplugin import IntervalTickPlugin
from valve.rcon import RCON, RCONError
from datetime import timedelta


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
            return None

        if self.server.running_time() <= timedelta(minutes=1):
            return None

        rcon_host     = self.server.multihome
        rcon_port     = self.thrall.conan_config.get(*CONAN_SETTINGS_MAPPING['RconPort'])
        rcon_password = self.thrall.conan_config.get(*CONAN_SETTINGS_MAPPING['RconPassword'])

        if not rcon_host or rcon_host in ('0.0.0.0'):
            rcon_host = '127.0.0.1'

        if not rcon_host or not rcon_port or not rcon_password:
            return None

        self.logger.debug('Executing on %s:%s %s' % (rcon_host, rcon_port, command))

        try:
            with RCON((rcon_host, int(rcon_port)), rcon_password) as rcon:
                return rcon.execute(command)
        except RCONError:
            self.logger.error('Error sending command ' + command)
        except Exception:
            self.logger.exception('Error when exceuting RCON command')

        return None

    def broadcast(self, message):
        return self.execute_safe('broadcast "%s"' % message)

    def tick_interval(self):
        pass
