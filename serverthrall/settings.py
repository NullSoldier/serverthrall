import os.path
import logging
import platform


STEAMCMD_PATH_MAC = os.path.join(os.getcwd(), 'vendor/steamcmd-mac/steamcmd')
STEAMCMD_PATH_WIN = os.path.join(os.getcwd(), 'vendor\\steamcmd-win\\steamcmd.exe')

CONAN_SERVER_APP_ID = '443030'
CONAN_CLIENT_APP_ID = '440900'
CONFIG_NAME = 'serverthrall.config'
CONAN_EXE_NAME = 'ConanSandboxServer.exe'

system = platform.system()
if system == 'Windows':
    STEAMCMD_PATH = STEAMCMD_PATH_WIN
elif system == 'Darwin':
    STEAMCMD_PATH = STEAMCMD_PATH_MAC
else:
    raise Exception('Platform not supported: %s' % platform)

# LOGGING
formatter = logging.Formatter('[%(name)s] %(message)s')

fileHandler = logging.FileHandler('serverthrall.log')
fileHandler.setFormatter(formatter)
fileHandler.setLevel(logging.DEBUG)

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(formatter)
consoleHandler.setLevel(logging.DEBUG)

thrall_logger = logging.getLogger('serverthrall')
thrall_logger.addHandler(fileHandler)
thrall_logger.addHandler(consoleHandler)
thrall_logger.setLevel(logging.DEBUG)

steamcmd_logger = logging.getLogger('serverthrall.steamcmd')
steamcmd_logger.setLevel(logging.DEBUG)

conan_config_logger = logging.getLogger('serverthrall.conan_config')
conan_config_logger.setLevel(logging.WARNING)
