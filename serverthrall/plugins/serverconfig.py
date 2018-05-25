from ..conanconfig import CONAN_SETTINGS_MAPPING
from .intervaltickplugin import IntervalTickPlugin
from .restartmanager import RestartManager
from configparser import NoOptionError
from contextlib import contextmanager
from datetime import timedelta
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
import os


class OnModifiedHandler(FileSystemEventHandler):

    def __init__(self, plugin, paths, logger, *args, **kwargs):
        super(OnModifiedHandler, self).__init__(*args, **kwargs)
        self.plugin = plugin
        self.paths = paths
        self.logger = logger
        self.ignore = False

    def on_modified(self, ev):
        if ev.src_path not in self.paths:
            return

        if self.ignore is True:
            return

        self.logger.debug('File %s: %s' % (ev.event_type, ev.src_path))
        self.plugin.tick_early()

    @contextmanager
    def ignore_modifications(self):
        self.ignore = True
        try:
            yield
        finally:
            self.ignore = True


class ServerConfig(IntervalTickPlugin):

    FIVE_MINUTES = 5 * 60

    def __init__(self, config):
        super(ServerConfig, self).__init__(config)
        config.set_default('interval.interval_seconds', self.FIVE_MINUTES)
        config.queue_save()

    def ready(self, *args, **kwargs):
        super(ServerConfig, self).ready(*args, **kwargs)
        self.stop_syncing = False

        self.restartmanager = self.thrall.get_plugin(RestartManager)
        self.restartmanager.register_offline_callback(self, self.on_server_offline)

        config_paths = self.get_conan_config_paths(self.thrall.conan_config)
        self.handler = OnModifiedHandler(self, config_paths, self.logger)

        default_config_dir = os.path.join(self.thrall.config.get_server_root(), 'ConanSandbox\\Config')
        derived_config_dir = os.path.join(self.thrall.config.get_server_root(), 'ConanSandbox\\Saved\\Config\\WindowsServer')

        self.observer = Observer()
        self.observer.schedule(self.handler, path=default_config_dir, recursive=False)
        self.observer.schedule(self.handler, path=derived_config_dir, recursive=False)
        self.observer.start()

        self.tick_early()

    def unload(self, *args, **kwargs):
        if self.observer is not None:
            self.observer.stop()
            self.observer.join()

    def quote_value(self, value):
        if not value.startswith('"'):
            value = '"' + value
        if not value.endswith('"'):
            value = value + '"'
        return value

    def unquote_value(self, value):
        if value.startswith('"'):
            value = value[1:]
        if value.endswith('"'):
            value = value[:-1]
        return value

    def get_conan_config_paths(self, conan_config):
        config_paths = []

        for group_name, group_paths in self.thrall.conan_config.group_paths.items():
            for group_path in group_paths:
                config_paths.append(group_path)

        return config_paths

    def get_config_value_safe(self, setting_name, setting_info):
        value = None

        try:
            value = self.config.get(setting_name)
        except NoOptionError:
            return None

        if value is not None:
            value = setting_info.transform(value)

        return value

    def sync(self):
        changed = False

        for setting_name, setting_info in CONAN_SETTINGS_MAPPING.items():

            dest_value = self.thrall.conan_config.get_setting(setting_info)
            source_value = self.get_config_value_safe(setting_name, setting_info)

            if source_value is None:
                continue

            if dest_value is not None:
                dest_value = setting_info.transform(dest_value)

            is_default = source_value == setting_info.default
            are_same = source_value == dest_value

            if dest_value is None and is_default:
                continue

            if setting_info.unquote:
                source_value = self.unquote_value(source_value)
                are_same |= self.unquote_value(source_value) == dest_value
                are_same |= self.quote_value(source_value) == dest_value

            if not are_same:
                path = self.thrall.conan_config.set_setting(setting_info, source_value, False)
                self.logger.info('Syncing %s=%s, %s' % (setting_info, source_value, path))
                changed = True

        return changed

    def try_safe_refresh(self):
        try:
            self.thrall.conan_config.refresh()
        except PermissionError:
            return False
        except FileNotFoundError:
            return False
        return True

    def on_server_offline(self):
        if not self.try_safe_refresh():
            self.logger.debug("Skipping config sync because conan has locked the configurations")
            return

        changed = self.sync()

        if changed:
            with self.handler.ignore_modifications():
                self.thrall.conan_config.save()

    def tick_interval(self):
        if self.stop_syncing:
            return

        if not self.try_safe_refresh():
            self.logger.debug("Skipping config sync because conan has locked the configurations")
            return

        if self.server.running_time() >= timedelta(seconds=self.interval_seconds):
            self.logger.warning("Skipping config sync because the server has been running for too long")
            self.stop_syncing = True
            self.back_off()
            return

        changed = self.sync()

        if changed:
            self.logger.info('Restarting server for config to take into affect')
            self.server.close()
            with self.handler.ignore_modifications():
                self.thrall.conan_config.save()
            self.server.start()
