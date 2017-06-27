# flake8: noqa
from .appconfig import config_load, ThrallConfig, PluginConfig
from .conanconfig import ConanConfig
from .conanserver import ConanServer
from .plugins import UptimeTracker, DownRecovery, ServerUpdater, RaidManager, ApiUploader
from .thrall import Thrall
from .steamcmd import SteamCmd
import settings
import ConfigParser
import os
import logging
import atexit

INSTALLED_PLUGINS = (
    UptimeTracker,
    DownRecovery,
    ServerUpdater,
    RaidManager,
    ApiUploader,
)

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
    additional_arguments = thrall_config.get('additional_arguments')
    server = ConanServer(server_path, steamcmd, additional_arguments)

if not server.is_installed():
    # Install the server if it's not installed
    logger.info('Conan server not installed, installing.')
    server.install_or_update()
elif thrall_config.getboolean('force_update_on_launch'):
    # user can force an update on launch if files are missing
    logger.info('Forcing update because you told me to do so in your configuration.')
    server.install_or_update()

# Load the unreal engine configs for the server
conan_config = ConanConfig(thrall_config.get('conan_server_directory'))

# Initialize and configure plugins
plugins = []
for plugin_class in INSTALLED_PLUGINS:
    logger.info('Initializing with plugin %s' % plugin_class.__name__)
    plugin_config = PluginConfig(plugin_class, config)
    plugin = plugin_class(plugin_config)
    plugins.append(plugin)

thrall = Thrall(steamcmd, thrall_config, conan_config, plugins, server)
def onExit():
    logger.info('Safely shutting down server thrall...')
    thrall.stop()
atexit.register(onExit)
thrall.start()
