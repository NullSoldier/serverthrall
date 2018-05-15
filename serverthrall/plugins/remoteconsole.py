from ..conanconfig import CONAN_SETTINGS_MAPPING
from .intervaltickplugin import IntervalTickPlugin
from contextlib import contextmanager
from valve.rcon import RCON, RCONError
from string import Template


class RemoteConsole(IntervalTickPlugin):

    ONE_MINUTE = 60
    TWO_MINUTES = 2 * 60

    def __init__(self, config):
        config.set_default('enabled', 'false')
        super(RemoteConsole, self).__init__(config)
        config.set_default('interval.interval_seconds', self.ONE_MINUTE)
        config.queue_save()

    def ready(self, *args, **kwargs):
        super(RemoteConsole, self).ready(*args, **kwargs)

        self.rcon_host     = self.server.multihome
        self.rcon_port     = int(self.thrall.conan_config.get(*CONAN_SETTINGS_MAPPING['RconPort']))
        self.rcon_password = self.thrall.conan_config.get(*CONAN_SETTINGS_MAPPING['RconPassword'])

    @contextmanager
    def get_rcon(self):
        with RCON((self.rcon_host, self.rcon_port), self.rcon_password) as rcon:
            yield rcon

    def execute_safe(self, command):
        if not self.enabled:
            return

        self.logger.debug('Executing: ' + command)

        try:
            with self.get_rcon() as rcon:
                return rcon.execute(command)
        except RCONError:
            self.logger.error('Error sending command ' + command)

    def broadcast(self, message, mapping=None):
        if mapping is not None:
            message = Template(message).safe_substitute(mapping)

        return self.execute_safe('broadcast "%s"' % message)

    def tick_interval(self):
        pass
