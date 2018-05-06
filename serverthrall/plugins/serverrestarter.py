from .discord import Discord
from .intervaltickplugin import IntervalTickPlugin
import datetime


class ServerRestarter(IntervalTickPlugin):

    ONE_MINUTE = 60

    def __init__(self, config):
        config.set_default('enabled', 'false')
        super(ServerRestarter, self).__init__(config)
        config.set_default('interval.interval_seconds', self.ONE_MINUTE)
        config.set_default('restart_times', '')
        config.set_default('warning_minutes', 5)
        config.set_default('send_warning_message', True)
        config.queue_save()

    def ready(self, steamcmd, server, thrall):
        super(ServerRestarter, self).ready(steamcmd, server, thrall)
        self.discord = thrall.get_plugin(Discord)

        self.warning_minutes = self.config.getint('warning_minutes')
        self.send_warning_message = self.config.getboolean('send_warning_message')
        self.last_restart_day = datetime.date.today() - datetime.timedelta(days=1)
        self.restart_times = self.get_restart_times(self.config.get('restart_times'))
        self.restart_dates = []
        self.messaged_warning = False

        self.ensure_dates_added()
        self.tick_early()
        self.log_restart_times()

    def log_restart_times(self):
        self.logger.debug("Restart Times")

        for date in self.restart_dates:
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
        return [datetime.datetime.combine(date, time) for time in times]

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

    def get_past_time(self):
        past_time = None

        return past_time

    def restart_server(self):
        if self.discord is not None:
            self.discord.send_message('ServerRestarter', 'The server is being restarted now.')

        self.logger.info('The server is being restarted now.')
        self.server.close()
        self.server.start()

    def send_restart_warning(self, minutes):
        message = 'The server is being restarted in %s minutes.' % minutes
        self.logger.info(message)

        if self.discord is not None:
            self.discord.send_message('ServerRestarter', message)

    def tick(self):
        now = datetime.datetime.now()
        past_time = None

        # handle clock jumping forward
        while now > self.restart_dates[0]:
            past_time = self.restart_dates[0]
            del self.restart_dates[0]
            self.ensure_dates_added()

        if past_time is not None:
            self.messaged_warning = False
            self.restart_server()

        warning_threshold = self.restart_dates[0] - datetime.timedelta(minutes=self.warning_minutes)

        if self.send_warning_message and not self.messaged_warning and now > warning_threshold:
            minutes = int((self.restart_dates[0] - datetime.datetime.now()).seconds / 60)
            self.send_restart_warning(minutes)
            self.messaged_warning = True
