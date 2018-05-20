from .intervaltickplugin import IntervalTickPlugin
from configparser import NoOptionError
from contextlib import contextmanager
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from ..conanconfig import CONAN_SETTINGS_MAPPING
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
    AUTO_QUOTE_ITEMS = ['ServerName']

    def __init__(self, config):
        super(ServerConfig, self).__init__(config)
        config.set_default('interval.interval_seconds', self.FIVE_MINUTES)
        config.queue_save()

    def ready(self, *args, **kwargs):
        super(ServerConfig, self).ready(*args, **kwargs)

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

    def get_conan_config_paths(self, conan_config):
        config_paths = []

        for group_name, group_paths in self.thrall.conan_config.group_paths.items():
            for group_path in group_paths:
                config_paths.append(group_path)

        return config_paths

    def get_config_value_safe(self, src):
        try:
            return self.config.get(src)
        except NoOptionError:
            return None

    def sync(self):
        changed = False

        for src, dest in CONAN_SETTINGS_MAPPING.items():
            group, section, option = dest

            value = self.get_config_value_safe(src)
            original = self.thrall.conan_config.get(group, section, option)

            if value is not None and value != original:
                if src in self.AUTO_QUOTE_ITEMS:
                    value = self.quote_value(value)

                path = self.thrall.conan_config.set(group, section, option, value, True)
                self.logger.info('Syncing %s.%s=%s, %s' % (section, option, value, path))

                path = self.thrall.conan_config.set(group, section, option, value, False)
                self.logger.info('Syncing %s.%s=%s, %s' % (section, option, value, path))

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

    def tick_interval(self):
        if not self.try_safe_refresh():
            self.logger.debug("Skipping config sync because conan has locked the configurations")
            return

        changed = self.sync()

        if changed:
            self.logger.info('Restarting server for config to take into affect')
            self.server.close()
            with self.handler.ignore_modifications():
                self.thrall.conan_config.save()
            self.server.start()
