from .exceptions import UnloadPluginException
import logging
import time
from .localization import Localization


class Thrall(object):

    def __init__(self, steamcmd, config, conan_config, plugins, server):
        self.steamcmd = steamcmd
        self.config = config
        self.conan_config = conan_config
        self.plugins = plugins
        self.server = server
        self.localization = Localization(config)
        self.logger = logging.getLogger('serverthrall')

    def get_plugin(self, type):
        for plugin in self.plugins:
            if isinstance(plugin, type):
                return plugin
        return None

    def unload_plugin(self, plugin, exception=None):
        if exception is not None:
            try:
                raise exception
            except:
                self.logger.exception('Unloading %s plugin after error ' % plugin.name)

        self.plugins.remove(plugin)
        plugin.unload()

    def stop(self):
        self.logger.info('Stopping ServerThrall')

    def start(self):
        if not self.server.is_running():
            self.server.start()
            self.conan_config.refresh()

        self._load_plugins()
        self.config.save_if_queued()

        while True:
            self._tick_plugins()
            self.config.save_if_queued()
            time.sleep(0.16)

    def _tick_plugins(self):
        for plugin in self.plugins:
            if not plugin.enabled:
                continue

            try:
                plugin.tick()
            except UnloadPluginException:
                self.plugins.remove(plugin)
                plugin.unload()
            except Exception:
                self.logger.exception('Unloading %s plugin after error ' % plugin.name)
                self.plugins.remove(plugin)
                plugin.unload()

    def _load_plugins(self):
        for plugin in self.plugins:
            if plugin.enabled:
                try:
                    plugin.ready(self.server, self.steamcmd, self)
                except UnloadPluginException:
                    self.unload_plugin(plugin)
                except Exception as ex:
                    self.unload_plugin(plugin, ex)
