import subprocess
import psutil
import time
from . import settings
import os
import logging


class ConanServer():

    def __init__(self, path, steamcmd, arguments, high_priority):
        self.path = path
        self.steamcmd = steamcmd
        self.arguments = arguments
        self.high_priority = high_priority
        self.logger = logging.getLogger('serverthrall')
        self.process = None

    def is_running(self):
        if self.process is None:
            return False
        return self.process.is_running()

    def is_installed(self):
        return os.path.exists(self.path)

    def install_or_update(self):
        directory = os.path.dirname(self.path)
        self.steamcmd.update_app(settings.CONAN_SERVER_APP_ID, directory)

    def start(self):
        if self.process or self.is_running():
            self.logger.error('Server already running call close_server first')
            return

        if len(self.arguments) == 0:
            self.logger.info('Launching server and waiting for child processes')
        else:
            self.logger.info('Launching server and waiting for child processes with extra arguments, %s' % self.arguments)

        try:
            process = subprocess.Popen([self.path, '-log', self.arguments])
            process = psutil.Process(process.pid)
            self.attach(process)
        except subprocess.CalledProcessError as ex:
            self.logger.exception('Server failed to start... %s' % ex)
            return False
        except psutil.NoSuchProcess as ex:
            self.logger.exception('Server started but crashed shortly after... %s' % ex)
            return False

        self.logger.info('Server running successfully')
        return True

    def close(self):
        if self.process is not None and self.process.is_running():
            self.process.terminate()
        self.process = None

    def attach(self, root_process):
        # TODO: remove this hack
        while len(root_process.children()) == 0:
            time.sleep(5)
        self.process = root_process.children()[0]

        if self.high_priority:
            self.logger.info('Setting server process to high priority')
            self.process.nice(psutil.HIGH_PRIORITY_CLASS)
            root_process.nice(psutil.HIGH_PRIORITY_CLASS)

    @staticmethod
    def create_from_running(config, steamcmd):
        logger = logging.getLogger('serverthrall')

        for p in psutil.process_iter():
            if p.name() == settings.CONAN_EXE_NAME:
                executable_path = p.exe()
                running_path = os.path.dirname(executable_path)
                expected_path = config.get('conan_server_directory')
                additional_arguments = config.get('additional_arguments')
                high_priority = config.getboolean('set_high_priority')

                # TODO: the to_lower hack does not work on linux
                if running_path.lower() != expected_path.lower():
                    logger.info('Found running server that is different than config')
                    continue

                logger.info('Found running server, attaching')
                server = ConanServer(executable_path, steamcmd, additional_arguments, high_priority)
                server.attach(p)
                return server

        return None
