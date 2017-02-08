import json
import subprocess
import time
import atexit
import psutil
import steamcmd


STEAM_CMD_PATH = "steamcmd.exe"
CONAN_PATH = "G:\\conanserver\\"
CONAN_SERVER_PATH = "G:\\conanserver\\ConanSandboxServer.exe"
CONAN_EXILES_APP_ID = 443030

DEFAULT_CONFIG = {'build_id': 0}


def save_config(config):
    print 'Saving config', config
    with open('config.json', 'w') as config_file:
        json.dump(config, config_file)


def load_config():
    config = None
    with open('config.json', 'w+') as config_file:
        try:
            config = json.load(config_file)
        except ValueError:
            print 'No config found, creating new config'
            return (DEFAULT_CONFIG, True)
    return (config, False)


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
        print config

        if was_created:
            save_config(config)

        i = 0

        while True:
            is_available, current, target = self.is_update_available()

            if self.server is None:
                self.start_server()

            if is_available:
                print 'An update is available from build %s to %s' % (current, target)
                self.close_server() 
                self.update_server()
                self.start_server()

            i = i + 1
            if i == 2:
                raise Exception('hello');
            time.sleep(5)


daemon = Daemon()
atexit.register(daemon.teardown)
daemon.run()