import subprocess
import time
import psutil
import steamcmd
from config import load_config, save_config


STEAM_CMD_PATH = "steamcmd.exe"
CONAN_PATH = "G:\\conanserver\\"
CONAN_SERVER_PATH = "G:\\conanserver\\ConanSandboxServer.exe"
CONAN_EXILES_APP_ID = 443030


class Daemon(object):

    def __init__(self):
        self.config = None
        self.server = None

    def is_update_available(self):
        app_info = steamcmd.get_app_info(CONAN_EXILES_APP_ID)
        current = int(self.config['build_id'])
        latest = int(app_info['443030']['extended']['depots']['branches']['public']['buildid'])
        return latest > current, current, latest

    def update_server(self):
        steamcmd.update_app(CONAN_EXILES_APP_ID, CONAN_PATH)
        app_info = steamcmd.get_app_info(CONAN_EXILES_APP_ID)
        self.config['build_id'] = app_info['443030']['extended']['depots']['branches']['public']['buildid']
        save_config(self.config)

    def start_server(self):
        if self.server:
            raise Exception('Server already running call close_server first')

        print 'Launching server and waiting for child processes'
        process = subprocess.Popen([CONAN_SERVER_PATH, '-log'])
        process = psutil.Process(process.pid)

        # TODO: remove this hack
        while len(process.children()) == 0:
            time.sleep(5)

        print 'Server running successfully'
        self.server = process.children()[0]

    def close_server(self):
        if self.server is not None:
            self.server.terminate()
            self.server = None

    def teardown(self):
        print 'Tearing down daemon'
        self.close_server()

    def run(self):
        config, was_created = load_config()
        self.config = config

        if was_created:
            save_config(self.config)

        while True:
            is_available, current, target = self.is_update_available()

            if self.server is None:
                self.start_server()

            if is_available:
                print 'An update is available from build %s to %s' % (current, target)
                self.close_server()
                self.update_server()
                self.start_server()

            time.sleep(5)
