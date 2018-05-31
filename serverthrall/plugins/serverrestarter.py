from .intervaltickplugin import IntervalTickPlugin
from .restartmanager import RestartManager
from string import Template
from datetime import date, datetime, timedelta, time


class ServerRestarter(IntervalTickPlugin):

    ONE_MINUTE = 60

    def __init__(self, config):
        config.set_default('enabled', 'false')
        super(ServerRestarter, self).__init__(config)
        config.set_default('interval.interval_seconds', self.ONE_MINUTE)
        config.set_default('restart_times', '')
        config.set_default('force_restart_on_launch', False)
        config.queue_save()

    def ready(self, steamcmd, server, thrall):
        super(ServerRestarter, self).ready(steamcmd, server, thrall)

        self.restartmanager = self.thrall.get_plugin(RestartManager)
        self.last_restart_day = date.today() - timedelta(days=1)
        self.restart_dates = []

        self.restart_times, invalid_times = self.config.gettimearray('restart_times')
        self.restart_times = sorted(self.restart_times, key=lambda t: (t.hour) * 60 + t.second)

        for invalid_time in invalid_times:
            self.logger.error('Expected time in HH:MM format (4:12) but got %s' % invalid_time)

        self.ensure_dates_added()

        if self.config.getboolean('force_restart_on_launch'):
            self.config.set('force_restart_on_launch', False)
            self.config.queue_save()
            self.restart_dates = [datetime.now()] + self.restart_dates

        # Log restart times
        self.logger.debug("Next Restart Times:")
        for restart_date in self.restart_dates[:5]:
            actual = restart_date + timedelta(minutes=self.restartmanager.warning_minutes)
            self.logger.debug(actual.strftime("%d/%m/%y %I:%M %p"))

        self.tick_early()

    def ensure_dates_added(self):
        now = datetime.now()

        if len(self.restart_times) == 0:
            return

        while len(self.restart_dates) < len(self.restart_times) * 2:
            self.last_restart_day = self.last_restart_day + timedelta(days=1)

            restart_dates = self.get_restart_dates(
                self.last_restart_day,
                self.restart_times,
                self.restartmanager.warning_minutes)

            for restart_date in restart_dates:
                if restart_date > now:
                    self.restart_dates.append(restart_date)

    def get_restart_dates(self, restart_date, restart_times, warning_minutes):
        return [datetime.combine(restart_date, t) - timedelta(minutes=warning_minutes) for t in restart_times]

    def get_restart_messages(self):
        default_message = 'The server is being restarted now.'
        discord_message = default_message
        rcon_message = default_message

        if self.config.has_option_filled('discord_restart_message'):
            discord_message = self.config.get('discord_restart_message')

        if self.config.has_option_filled('rcon_restart_message'):
            rcon_message = self.config.get('rcon_restart_message')

        next_restart_string = self.thrall.localization.return_word('never')
        if len(self.restart_dates) > 0:
            next_restart_string = self.restart_dates[0].strftime("%I:%M %p")

        template = {
            'nextrestart': next_restart_string,
        }

        discord_message = Template(discord_message).safe_substitute(template)
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
        while len(self.restart_dates) > 0 and datetime.now() > self.restart_dates[0]:
            past_time = self.restart_dates[0]
            del self.restart_dates[0]
            self.ensure_dates_added()

        if past_time is not None:
            discord_warning, rcon_warning = self.get_warning_messages()
            discord_restart, rcon_restart = self.get_restart_messages()

            self.restartmanager.start_restart(
                plugin=self,
                rcon_warning=rcon_warning,
                rcon_restart=rcon_restart,
                discord_warning=discord_warning,
                discord_restart=discord_restart)
