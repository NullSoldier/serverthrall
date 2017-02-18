import subprocess
import psutil
import time
import settings
import os

class ConanServer():

    def __init__(self, path, steamcmd):
        self.path = path
        self.steamcmd = steamcmd
        self.process = None

    def is_running(self):
        if self.process is None:
            return False
        return self.process.is_running()

    def is_installed(self):
        return os.path.exists(self.path)

    def start(self):
        if self.process or self.is_running():
            raise Exception('Server already running call close_server first')

        print 'Launching server and waiting for child processes'
        try:
            process = subprocess.Popen([self.path, '-log'])
            process = psutil.Process(process.pid)
        except subprocess.CalledProcessError as ex:
            print 'Server failed to start... %s' % ex
            return False

        self.attach(process)
        print 'Server running successfully'
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
        for p in psutil.process_iter():
            if p.name() == settings.CONAN_EXE_NAME:
                executable_path = p.exe()
                running_path = os.path.dirname(executable_path)
                expected_path = config.get('conan_server_directory')

                # TODO: the to_lower hack does not work on linux
                if running_path.lower() != expected_path.lower():
                    print 'Found running server that is different than config'
                else:
                    print 'Found running server, attaching'
                    server = ConanServer(executable_path, steamcmd)
                    server.attach(p)
                    return server
        return None
