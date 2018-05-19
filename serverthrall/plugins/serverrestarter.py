from .intervaltickplugin import IntervalTickPlugin
from .restartmanager import RestartManager
from string import Template
import datetime


class ServerRestarter(IntervalTickPlugin):

    ONE_MINUTE = 60

    def __init__(self, config):
        config.set_default('enabled', 'false')
        super(ServerRestarter, self).__init__(config)
        config.set_default('interval.interval_seconds', self.ONE_MINUTE)
        config.set_default('restart_times', '')
        config.queue_save()

    def ready(self, steamcmd, server, thrall):
        super(ServerRestarter, self).ready(steamcmd, server, thrall)

        self.restartmanager = self.thrall.get_plugin(RestartManager)
        self.last_restart_day = datetime.date.today() - datetime.timedelta(days=1)
        self.restart_times = self.get_restart_times(self.config.get('restart_times'))
        self.restart_dates = []

        self.ensure_dates_added()
        self.tick_early()

        # Log restart times
        self.logger.debug("Next Restart Times:")
        for date in self.restart_dates[:5]:
            self.logger.debug(date.strftime("%d/%m/%y %I:%M %p"))

    def ensure_dates_added(self):
        now = datetime.datetime.now()

        while len(self.restart_dates) < len(self.restart_times) * 2:
            self.last_restart_day = self.last_restart_day + datetime.timedelta(days=1)

            restart_dates = self.get_restart_dates(self.last_restart_day, self.restart_times)

            for restart_date in restart_dates:
                if restart_date > now:
                    self.restart_dates.append(restart_date)

    def get_restart_dates(self, date, times):
        return [datetime.datetime.combine(date, t) for t in times]

    def get_restart_times(self, restart_times_config):
        times_option = restart_times_config
        times_splits = times_option.strip().split(',')

        times = []

        for time_split in times_splits:
            parts = time_split.strip().split(':')
            hour = None
            minute = 0

            if len(parts) > 0:
                hour = int(parts[0])

            if len(parts) > 1:
                minute = int(parts[1])

            if hour is None or minute is None:
                self.config.error('Expected time in HH:MM format (04:20) but got %s' % time_split)
                continue

            times.append(datetime.time(hour=hour, minute=minute))

        return sorted(times, key=lambda time: (time.hour) * 60 + time.second)

    def get_restart_messages(self):
        default_message = 'The server is being restarted now.'
        discord_message = default_message
        rcon_message = default_message

        if self.config.has_option_filled('discord_restart_message'):
            discord_message = self.config.get('discord_restart_message')

        if self.config.has_option_filled('rcon_restart_message'):
            rcon_message = self.config.get('rcon_restart_message')

        template = {
            'nextrestart': self.restart_dates[0].strftime("%I:%M %p"),
        }

        discord_message = Template(discord_message).safe_substitute(template),
        rcon_message = Template(rcon_message).safe_substitute(template)

        return discord_message, rcon_message

    def get_warning_messages(self):
        default_message = 'The server is being restarted in $timeleft $timeunit.'
        discord_message = default_message
        rcon_message = default_message

        if self.config.has_option_filled('discord_warning_message'):
            discord_message = self.config.get('discord_warning_message')

        if self.config.has_option_filled('rcon_warning_message'):
            rcon_message = self.config.get('rcon_warning_message')

        return discord_message, rcon_message

    def tick(self):
        past_time = None

        # handle clock jumping forward
        while datetime.datetime.now() > self.restart_dates[0]:
            past_time = self.restart_dates[0]
            del self.restart_dates[0]
            self.ensure_dates_added()

        if past_time is not None:
            rcon_warning, discord_warning = self.get_warning_messages()
            rcon_restart, discord_restart = self.get_restart_messages()

            self.restartmanager.start_restart(
                plugin=self,
                rcon_warning=rcon_warning,
                rcon_restart=rcon_restart,
                discord_warning=discord_warning,
                discord_restart=discord_restart)
