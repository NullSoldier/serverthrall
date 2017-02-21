from .conanconfig import ConanConfig
import subprocess
import psutil
import time
import settings
import os
import logging


class ConanServer():

    def __init__(self, path, steamcmd):
        self.path = path
        self.steamcmd = steamcmd
        self.process = None
        self.logger = logging.getLogger('serverthrall')

    def is_running(self):
        if self.process is None:
            return False
        return self.process.is_running()

    def is_installed(self):
        return os.path.exists(self.path)

    def install_or_update(self):
        directory = os.path.dirname(self.path)
        self.steamcmd.update_app(settings.CONAN_APP_ID, directory)

    def start(self):
        if self.process or self.is_running():
            raise Exception('Server already running call close_server first')

        self.logger.info('Launching server and waiting for child processes')
        try:
            process = subprocess.Popen([self.path, '-log'])
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

    def attach(self, process):
        # TODO: remove this hack
        while len(process.children()) == 0:
            time.sleep(5)
        self.process = process.children()[0]

    @staticmethod
    def create_from_running(config, steamcmd):
        logger = logging.getLogger('serverthrall')

        for p in psutil.process_iter():
            if p.name() == settings.CONAN_EXE_NAME:
                executable_path = p.exe()
                running_path = os.path.dirname(executable_path)
                expected_path = config.get('conan_server_directory')

                # TODO: the to_lower hack does not work on linux
                if running_path.lower() != expected_path.lower():
                    logger.info('Found running server that is different than config')
                else:
                    logger.info('Found running server, attaching')
                    server = ConanServer(executable_path, steamcmd)
                    server.attach(p)
                    return server

        return None
