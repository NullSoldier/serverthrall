from .appconfig import config_load, ThrallConfig, PluginConfig
from .conanconfig import ConanConfig
from .conanserver import ConanServer
from .plugins import UptimeTracker, DownRecovery, ServerUpdater, ApiUploader, ServerConfig, DeadManSnitch
from .steamcmd import SteamCmd
from .thrall import Thrall
from configparser import ConfigParser
import atexit
import logging
import os
import sys
from . import settings

INSTALLED_PLUGINS = (
    ServerConfig,
    UptimeTracker,
    DownRecovery,
    ServerUpdater,
    ApiUploader,
    DeadManSnitch
)

def run_server_thrall():
    logger = logging.getLogger('serverthrall')
    logger.debug('Starting serverthrall with python %s.%s.%s' % (
        sys.version_info[0],
        sys.version_info[1],
        sys.version_info[2]))

    config = config_load()
    config_is_new = False

    if config is None:
        logger.info('No config found, creating for the first time')
        config = ConfigParser()
        config.optionxform = str
        config_is_new = True

    steamcmd = SteamCmd(settings.STEAMCMD_PATH)
    thrall_config = ThrallConfig(config)

    if config_is_new:
        thrall_config.save()

    # Load the unreal engine configs for the server
    conan_config = ConanConfig(thrall_config.get('conan_server_directory'))

    # Try to attach to a running server before launching a new one
    server = ConanServer.create_from_running(thrall_config, steamcmd)

    # Create the server if we could not attach to a running process
    if server is None:
        additional_arguments = thrall_config.get('additional_arguments')
        set_high_priority = thrall_config.getboolean('set_high_priority')

        server_path = os.path.join(
            thrall_config.get('conan_server_directory'),
            thrall_config.get('conan_exe_name'))

        server = ConanServer(server_path, steamcmd, additional_arguments, set_high_priority)

    if not server.is_installed():
        # Install the server if it's not installed
        logger.info('Conan server not installed, installing.')
        server.close()
        server.install_or_update()
        server.start()
        conan_config.wait_for_configs_to_exist()
        conan_config.refresh()

    elif thrall_config.getboolean('force_update_on_launch'):
        # user can force an update on launch if files are missing
        logger.info('Forcing update because you told me to do so in your configuration.')
        server.close()
        server.install_or_update()
        server.start()
        conan_config.wait_for_configs_to_exist()
        conan_config.refresh()

    else:
        conan_config.wait_for_configs_to_exist()
        conan_config.refresh()

    # Initialize and configure plugins
    plugins = []
    for plugin_class in INSTALLED_PLUGINS:
        logger.info('Initializing with plugin %s' % plugin_class.__name__)
        plugin_config = PluginConfig(plugin_class, config, thrall_config)
        plugin = plugin_class(plugin_config)
        plugins.append(plugin)

    thrall = Thrall(steamcmd, thrall_config, conan_config, plugins, server)
    def on_exit():
        logger.info('Safely shutting down server thrall...')
        thrall.stop()
    atexit.register(on_exit)
    thrall.start()
