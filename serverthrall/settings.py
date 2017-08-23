import os.path
import logging

STEAMCMD_PATH = os.path.join(os.getcwd(), 'vendor\\steamcmd\\steamcmd.exe')
CONAN_SERVER_APP_ID = '443030'
CONAN_CLIENT_APP_ID = '440900'
CONFIG_NAME = 'serverthrall.config'

# LOGGING
consoleFormatter = logging.Formatter('[%(name)s] %(message)s')
fileFormatter = logging.Formatter("[%(asctime)s|%(levelname)s|%(name)s] %(message)s", "%Y-%m-%d %H:%M:%S")

fileHandler = logging.FileHandler('serverthrall.log')
fileHandler.setFormatter(fileFormatter)
fileHandler.setLevel(logging.DEBUG)

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(consoleFormatter)
consoleHandler.setLevel(logging.DEBUG)

thrall_logger = logging.getLogger('serverthrall')
thrall_logger.addHandler(fileHandler)
thrall_logger.addHandler(consoleHandler)
thrall_logger.setLevel(logging.DEBUG)

steamcmd_logger = logging.getLogger('serverthrall.steamcmd')
steamcmd_logger.setLevel(logging.WARNING)

conan_config_logger = logging.getLogger('serverthrall.conan_config')
conan_config_logger.setLevel(logging.INFO)
