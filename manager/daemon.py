import subprocess
import time
import psutil
from steamcmd import SteamCmd
from config import load_config, save_config
import os


DEFAULT_CONFIG = {
    'build_id': 0,
    'app_id': 443030,
    'steamcmd_path': os.path.join(os.getcwd(), 'steamcmd\\steamcmd.exe'),
    'conan_dir': os.path.join(os.getcwd(), 'conanserver\\'),
    'conan_path': os.path.join(os.getcwd(), 'conanserver\\ConanSandboxServer.exe'),
}


class Daemon(object):

    def __init__(self):
        super(Daemon, self).__init__()
        self.config = None
        self.server = None
        self.steamcmd = None

    def is_update_available(self):
        app_info = self.steamcmd.get_app_info(self.config['app_id'])
        current = int(self.config['build_id'])
        latest = int(app_info['443030']['extended']['depots']['branches']['public']['buildid'])
        return latest > current, current, latest

    def update_server(self):
        self.steamcmd.update_app(
            self.config['app_id'],
            self.config['conan_dir'])

        app_info = self.steamcmd.get_app_info(self.config['app_id'])
        self.config['build_id'] = app_info['443030']['extended']['depots']['branches']['public']['buildid']
        save_config(self.config)

    def start_server(self):
        if self.server:
            raise Exception('Server already running call close_server first')

        print 'Launching server and waiting for child processes'
        try:
            process = subprocess.Popen([self.config['conan_path'], '-log'])
            process = psutil.Process(process.pid)
        except subprocess.CalledProcessError as ex:
            print 'Server failed to start... %s' % ex
            return False

        # TODO: remove this hack
        while len(process.children()) == 0:
            time.sleep(5)

        print 'Server running successfully'
        self.server = process.children()[0]
        return True

    def close_server(self):
        if self.server is not None and self.server.is_running():
            self.server.terminate()
        self.server = None

    def teardown(self):
        print 'Tearing down daemon'
        self.close_server()

    def run(self):
        self.config = load_config()

        if self.config is None:
            print 'No config found, creating new config'
            self.config = DEFAULT_CONFIG
            save_config(self.config)

        self.steamcmd = SteamCmd(self.config['steamcmd_path'])

        while True:
            is_available, current, target = self.is_update_available()

            if is_available:
                print 'An update is available from build %s to %s' % (current, target)
                self.close_server()
                self.update_server()
                self.start_server()

            if self.server and not self.server.is_running():
                print 'Server down... rebooting'
                self.close_server()
                self.start_server()

            if self.server is None:
                self.start_server()

            time.sleep(5)
