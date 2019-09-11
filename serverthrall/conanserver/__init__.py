from serverthrall import settings
from datetime import datetime, timedelta
import logging
import os
import psutil
import subprocess
import socket
from .windows import close_server_windows

# The estimated time it rougly takes a server to start up and properly respond to CTRL+C events
IS_RESPONSIVE_HUERISTIC = timedelta(minutes=2)

class ConanServer():

    def __init__(self, server_root, server_path, steamcmd, arguments, high_priority, multihome, use_testlive):
        self.server_root = server_root
        self.server_path = server_path
        self.steamcmd = steamcmd
        self.arguments = arguments
        self.high_priority = high_priority
        self.use_testlive = use_testlive
        self.logger = logging.getLogger('serverthrall')
        self.process = None
        self.multihome = multihome
        self.start_time = None

        if not self.multihome:
            self.multihome = socket.gethostbyname(socket.gethostname())

        if self.multihome:
            self.arguments = self.arguments + " -MULTIHOME=" + self.multihome

        self.arguments = self.arguments.strip()

    def is_running(self):
        if self.process is None:
            return False
        return self.process.is_running()

    def is_installed(self):
        return os.path.exists(self.server_path)

    def running_time(self):
        if self.start_time is None:
            return timedelta()
        return datetime.now() - self.start_time

    def install_or_update(self):
        self.steamcmd.update_app(
            app_id=settings.CONAN_SERVER_APP_ID,
            app_dir=self.server_root,
            beta='testlive' if self.use_testlive else None)

    def start(self):
        if self.process or self.is_running():
            self.logger.error('Server already running call close_server first')
            return

        if len(self.arguments) == 0:
            self.logger.info('Launching server and waiting for child processes')
        else:
            self.logger.info('Launching server and waiting for child processes with extra arguments, %s' % self.arguments)

        try:
            process = subprocess.Popen([self.server_path, self.arguments])
            process = psutil.Process(process.pid)
            self.attach(process)
        except subprocess.CalledProcessError as ex:
            self.logger.exception('Server failed to start... %s' % ex)
            return False
        except psutil.NoSuchProcess as ex:
            self.logger.exception('Server started but crashed shortly after... %s' % ex)
            return False

        self.start_time = datetime.now()
        self.logger.info('Server running successfully')
        return True

    def close(self, kill=False):
        if not kill and self.running_time() < IS_RESPONSIVE_HUERISTIC:
            self.logger.debug('Server was asked to close cleanly, forcing the server to terminate because its probably not responsive')
            kill = True

        if not kill:
            # Try windows safe close first
            if self.process is not None and self.process.is_running():
                close_server_windows(self)

        # Hard kill the process if it's still running
        if self.process is not None and self.process.is_running():
            if not kill:
                self.logger.error('Server did not close cleanly, terminating.')

            self.process.terminate()
            self.wait_for_close()

        self.start_time = None
        self.process = None

    def wait_for_close(self, timeout=None):
        if self.process is None:
            return True

        (gone, alive) = psutil.wait_procs([self.process], timeout)
        return alive == 0

    def attach(self, root_process):
        self.process = root_process

        if self.high_priority:
            self.logger.info('Setting server process to high priority')
            self.process.nice(psutil.HIGH_PRIORITY_CLASS)
            root_process.nice(psutil.HIGH_PRIORITY_CLASS)

    @staticmethod
    def create_from_running(config, steamcmd):
        logger = logging.getLogger('serverthrall')

        for p in psutil.process_iter():

            try:
                process_name = p.name()
                process_exe_path = p.exe()
            except psutil.AccessDenied:
                continue

            if process_name == config.get_conan_exe_name():
                running_dir = os.path.dirname(process_exe_path)
                expected_dir = os.path.dirname(config.get_server_path())

                # TODO: the to_lower hack does not work on linux
                if running_dir.lower() != expected_dir.lower():
                    logger.info("Found running server that is different than config" +
                        "\nExpected: " + config.get_server_path().lower() +
                        "\nActual: " + process_exe_path.lower())
                    continue

                logger.info('Found running server, attaching')
                server = ConanServer(
                    server_root=config.get_server_root(),
                    server_path=process_exe_path,
                    steamcmd=steamcmd,
                    arguments=config.get('additional_arguments'),
                    high_priority=config.getboolean('set_high_priority'),
                    multihome=config.get('multihome'),
                    use_testlive=config.getboolean('testlive'))
                server.attach(p)
                server.start_time = datetime.min
                return server

        return None
