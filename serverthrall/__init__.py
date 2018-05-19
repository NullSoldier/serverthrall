from .appconfig import config_load, ThrallConfig, PluginConfig
from .conanconfig import ConanConfig
from .conanserver import ConanServer
from .plugins import UptimeTracker, DownRecovery, ServerUpdater, ApiUploader, ServerConfig, DeadManSnitch, ServerRestarter, Discord, RemoteConsole, RestartManager
from .steamcmd import SteamCmd
from .thrall import Thrall
from configparser import ConfigParser
import atexit
import logging
import sys
import traceback
from . import settings

INSTALLED_PLUGINS = (
    ApiUploader,
    DeadManSnitch,
    Discord,
    DownRecovery,
    RemoteConsole,
    ServerConfig,
    ServerRestarter,
    ServerUpdater,
    UptimeTracker,
    RestartManager
)

def run_server_thrall(app_version):
    logger = logging.getLogger('serverthrall')

    def unhandled_exception(exc_type, value, trace):
        logger.error("".join(traceback.format_exception(exc_type, value, trace)))

    sys.excepthook = unhandled_exception

    config = config_load()
    config_is_new = False

    if config is None:
        logger.info('No config found, creating for the first time')
        config = ConfigParser()
        config.optionxform = str
        config_is_new = True

    steamcmd = SteamCmd(settings.STEAMCMD_PATH)
    thrall_config = ThrallConfig(config)

    if app_version is not None:
        logger.info('Running version ' + app_version)
        thrall_config.set('version', app_version)

    if config_is_new:
        thrall_config.save()

    # Load the unreal engine configs for the server
    conan_config = ConanConfig(thrall_config.get_server_root())

    # Try to attach to a running server before launching a new one
    server = ConanServer.create_from_running(thrall_config, steamcmd)

    # Create the server if we could not attach to a running process
    if server is None:
        additional_arguments = thrall_config.get('additional_arguments')
        set_high_priority = thrall_config.getboolean('set_high_priority')
        multihome = thrall_config.get('multihome')
        use_testlive = thrall_config.getboolean('testlive')

        server = ConanServer(
            server_root=thrall_config.get_server_root(),
            server_path=thrall_config.get_server_path(),
            steamcmd=steamcmd,
            arguments=additional_arguments,
            high_priority=set_high_priority,
            multihome=multihome,
            use_testlive=use_testlive)

    if not server.is_installed():
        logger.info('Conan server not installed at %s, installing.' % server.server_path)
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
