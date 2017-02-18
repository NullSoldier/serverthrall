# flake8: noqa
from .appconfig import config_load, ThrallConfig, PluginConfig
from .conanserver import ConanServer
from .plugins import UptimeTracker, DownRecovery, ServerUpdater
from .thrall import Thrall
from .steamcmd import SteamCmd
import settings
import ConfigParser
import os
import logging
import atexit

logger = logging.getLogger('serverthrall')

config = config_load()
if config is None:
    logger.info('No config found, creating for the first time')
    config = ConfigParser.RawConfigParser()

steamcmd = SteamCmd(settings.STEAMCMD_PATH)
thrall_config = ThrallConfig(config)

# Try to attach to a running server before launching a new one
server = ConanServer.create_from_running(thrall_config, steamcmd)

# Create the server if we could not attach to a running process
if server is None:
    server_path = os.path.join(thrall_config.get('conan_server_directory'), settings.CONAN_EXE_NAME)
    server = ConanServer(server_path, steamcmd)

# Install the server if it's not installed
if not server.is_installed():
    logger.info('Conan server not installed, installing.')
    server.install_or_update()

# Initialize and configure plugins
plugins = []
for plugin_class in (UptimeTracker, DownRecovery, ServerUpdater):
    logger.info('Initializing with plugin %s' % plugin_class.__name__)
    plugin_config = PluginConfig(plugin_class, config)
    plugin = plugin_class(plugin_config)
    plugins.append(plugin)

thrall = Thrall(steamcmd, thrall_config, plugins, server)
def onExit():
    logger.info('Safely shutting down server thrall....')
    thrall.stop()
atexit.register(onExit)
thrall.start()
