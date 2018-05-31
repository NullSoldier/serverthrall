from .discord import Discord
from .intervaltickplugin import IntervalTickPlugin
from .remoteconsole import RemoteConsole
from datetime import datetime, timedelta
from string import Template
import time
from itertools import chain


class RestartInformation():

    def __init__(self, plugin, rcon_warning, rcon_restart, discord_warning, discord_restart, restart_time, warning_thresholds):
        self.plugin = plugin
        self.rcon_warning = rcon_warning
        self.rcon_restart = rcon_restart
        self.discord_warning = discord_warning
        self.discord_restart = discord_restart
        self.restart_time = restart_time
        self.warning_thresholds = warning_thresholds[:]

    def should_restart(self):
        return datetime.now() >= self.restart_time

    def should_send_warning(self):
        time_left = self.restart_time - datetime.now()
        time_left_minutes = int(time_left.seconds / 60)
        is_past = False

        while len(self.warning_thresholds) > 0 and time_left_minutes <= self.warning_thresholds[0]:
            is_past = True
            del self.warning_thresholds[0]

        return is_past


class RestartManager(IntervalTickPlugin):

    def __init__(self, config):
        super(RestartManager, self).__init__(config)
        self.enabled = True
        config.set_default('interval.interval_seconds', 60)
        config.set_default('warning_minutes', 10)
        config.set_default('warning_send_discord', True)
        config.set_default('warning_send_rcon', True)
        config.set_default('restart_send_discord', True)
        config.set_default('restart_send_rcon', True)
        config.queue_save()

        self.warning_thresholds = sorted(self.config.getintarray('warning_minutes'), reverse=True)
        self.warning_minutes = self.warning_thresholds[0]
        self.active_restart_info = None
        self.offline_callbacks = {}
        self.restart_callbacks = {}

    def ready(self, steamcmd, server, thrall):
        super(RestartManager, self).ready(steamcmd, server, thrall)
        self.warning_send_discord = self.config.getboolean('warning_send_discord')
        self.warning_send_rcon = self.config.getboolean('warning_send_rcon')
        self.restart_send_discord = self.config.getboolean('restart_send_discord')
        self.restart_send_rcon = self.config.getboolean('restart_send_rcon')

        self.discord = thrall.get_plugin(Discord)
        self.rcon = thrall.get_plugin(RemoteConsole)

    def notify_callbacks(self):
        callback_items = chain(
            self.offline_callbacks.items(),
            self.restart_callbacks.items())

        for plugin_name, (plugin, callback) in callback_items:
            try:
                callback()
            except Exception as ex:
                self.logger.error('Plugin %s failed to handle on offline callback' % plugin_name)
                self.thrall.unload_plugin(plugin, ex)

        self.restart_callbacks.clear()

    def register_offline_callback(self, plugin, offline_callback):
        if plugin.name not in self.offline_callbacks and offline_callback is not None:
            self.offline_callbacks[plugin.name] = (plugin, offline_callback)

    def register_restart_callback(self, plugin, restart_callback):
        if plugin.name not in self.restart_callbacks and restart_callback is not None:
            self.restart_callbacks[plugin.name] = (plugin, restart_callback)

    def start_restart(self, plugin, rcon_warning, rcon_restart, discord_warning, discord_restart, restart_callback=None):
        self.register_restart_callback(plugin, restart_callback)

        if self.active_restart_info is not None:
            return

        self.logger.info('Beginning restart for ' + plugin.name)

        self.active_restart_info = RestartInformation(
            plugin=plugin,
            rcon_warning=rcon_warning,
            rcon_restart=rcon_restart,
            discord_warning=discord_warning,
            discord_restart=discord_restart,
            restart_time=datetime.now() + timedelta(minutes=self.warning_minutes),
            warning_thresholds=self.warning_thresholds)

        self.tick_early()

    def get_message_templates(self, time_left):
        time_left_minutes = int(time_left.seconds / 60)

        if time_left_minutes == 1:
            time_unit = self.thrall.localization.return_word('minute')
        else:
            time_unit = self.thrall.localization.return_word('minutes')

        return {
            'timeleft': str(time_left_minutes),
            'timeunit': time_unit,
            'newline': '\n'
        }

    def send_warning_message(self):
        time_left = self.active_restart_info.restart_time - datetime.now()
        time_left_minutes = int(time_left.seconds / 60)
        template = self.get_message_templates(time_left)

        self.logger.info('The server is being restarted in %s minutes.' % time_left_minutes)

        if self.warning_send_rcon and self.rcon is not None:
            rcon_warning = self.active_restart_info.rcon_warning
            rcon_warning = Template(rcon_warning).safe_substitute(template)
            self.rcon.broadcast(rcon_warning)

        if self.warning_send_discord and self.discord is not None:
            discord_warning = self.active_restart_info.discord_warning
            discord_warning = Template(discord_warning).safe_substitute(template)
            self.discord.send_message(self.active_restart_info.plugin.name, discord_warning)

    def send_restart_message(self):
        template = self.get_message_templates(timedelta())

        if self.restart_send_rcon and self.rcon is not None:
            rcon_restart = self.active_restart_info.rcon_restart
            rcon_restart = Template(rcon_restart).safe_substitute(template)
            self.rcon.broadcast(rcon_restart)

        if self.restart_send_discord and self.discord is not None:
            discord_restart = self.active_restart_info.discord_restart
            discord_restart = Template(discord_restart).safe_substitute(template)
            self.discord.send_message(self.active_restart_info.plugin.name, discord_restart)

    def tick_interval(self):
        if self.active_restart_info is None:
            return

        if not self.active_restart_info.should_restart():
            if self.active_restart_info.should_send_warning():
                self.send_warning_message()
            return

        self.send_restart_message()
        time.sleep(1)
        self.active_restart_info = None
        self.server.close()
        self.notify_callbacks()
        self.server.start()
