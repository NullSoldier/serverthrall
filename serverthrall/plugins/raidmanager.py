from .thrallplugin import ThrallPlugin
from datetime import datetime, timedelta
import ConfigParser
import os


class RaidTimeSpan(object):

    def __init__(self, start_hour, length_in_hours):
        self.start = datetime(year=1900, month=1, day=1, hour=start_hour)
        self.end   = self.start + timedelta(hours=length_in_hours)

    def is_time_inside(self, value):
        # sample the current time on day 0 and 1 in case of time overflow
        sample1 = datetime(year=1900, month=1, day=1, hour=value.hour, minute=value.minute, second=value.second)
        sample2 = datetime(year=1900, month=1, day=2, hour=value.hour, minute=value.minute, second=value.second)

        return (
            (self.start <= sample1 and sample1 <= self.end) or
            (self.start <= sample2 and sample2 <= self.end))

    def format(self):
        return "%s to %s" % (
            self.start.strftime('%I:%M %p'),
            self.end.strftime('%I:%M %p'))


class RaidManager(ThrallPlugin):

    def __init__(self, config):
        super(RaidManager, self).__init__(config)
        self.config.set_default('start_hour', '17')
        self.config.set_default('length_in_hours', '5')

    def ready(self, steamcmd, server, thrall):
        super(RaidManager, self).ready(steamcmd, server, thrall)

        self.raidspan = RaidTimeSpan(
            self.config.getint('start_hour'),
            self.config.getint('length_in_hours'))

        is_on_formatted = 'ON' if self.thrall.conan_config.getboolean('ServerSettings', 'ServerSettings', 'CanDamagePlayerOwnedStructures') else 'OFF'

        self.logger.info('Raiding is currently %s in the server.' % is_on_formatted)
        self.logger.info('Raiding is enabled from %s' % self.raidspan.format())

    def tick(self):
        actual = self.thrall.conan_config.getboolean('ServerSettings', 'ServerSettings', 'CanDamagePlayerOwnedStructures')
        expected = self.raidspan.is_time_inside(datetime.now())

        if actual != expected:
            self.logger.info('Preparing to turn %s raiding.' % ('ON' if expected else 'OFF'))
            self.server.close()
            self.thrall.conan_config.setboolean('ServerSettings', 'ServerSettings', 'CanDamagePlayerOwnedStructures', expected)
            self.thrall.conan_config.save()
            self.server.start()
