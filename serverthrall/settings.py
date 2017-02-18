import os.path
import logging

STEAMCMD_PATH = os.path.join(os.getcwd(), 'vendor\\steamcmd\\steamcmd.exe')
CONAN_APP_ID = '443030'
CONFIG_NAME = 'serverthrall.config'
CONAN_EXE_NAME = 'ConanSandboxServer.exe'

# LOGGING
formatter = logging.Formatter('[%(name)s] %(message)s')

fileHandler = logging.FileHandler('serverthrall.log')
fileHandler.setFormatter(formatter)
fileHandler.setLevel(logging.DEBUG)

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(formatter)
consoleHandler.setLevel(logging.DEBUG)

logger = logging.getLogger('serverthrall')
logger.setLevel(logging.DEBUG)
logger.addHandler(fileHandler)
logger.addHandler(consoleHandler)
