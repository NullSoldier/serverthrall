import subprocess
import json
from steamfiles import acf
from .steamcmd import get_app_info, update_app
import signal
import psutil

STEAM_CMD_PATH = "G:\\steamcmd\\steamcmd.exe"
CONAN_PATH = "G:\\conanserver\\"
CONAN_SERVER_PATH = "G:\\conanserver\\ConanSandboxServer.exe"
CONAN_EXILES_APP_ID = 443030

DEFAULT_CONFIG = {
    'build_id': 0
}

config = None


def is_update_available(config):
    app_info = get_app_info(CONAN_EXILES_APP_ID)
    current = int(config['build_id'])
    latest = int(app_info['443030']['extended']['depots']['branches']['public']['buildid'])
    return latest > current, current, latest


def update_server():
    update_app(CONAN_EXILES_APP_ID, CONAN_PATH)

    app_info = get_app_info(CONAN_EXILES_APP_ID)
    config['build_id'] = app_info['443030']['extended']['depots']['branches']['public']['buildid']
    save_config(config)


def open_server():
    print 'Launching server and waiting for child processes'
    process = subprocess.Popen([CONAN_SERVER_PATH, '-log'], creationflags=subprocess.CREATE_NEW_PROCESS_GROUP);
    process = psutil.Process(process.pid)

    # TODO: remove this hack
    while len(process.children()) == 0:
        import time; time.sleep(5)

    print 'Server running successfully'
    return process.children()[0];


def close_server():
    pass


def save_config(config):
    with open('config.json', 'w') as config_file:
        print 'Saving config', config
        json.dump(config, config_file)


def load_config():
    config = None

    with open('config.json', 'w+') as config_file:
        try:
            config = json.load(config_file)
        except ValueError as ex:
            print 'No config found, creating new config'
            return (DEFAULT_CONFIG, True)

    return (config, False)


config, is_new = load_config()
if is_new:
    save_config(config)

server_process = None

while True:
    is_available, current, target = is_update_available(config)

    if server_process is None:
        server_process = open_server()

    if is_available:
        print 'An update is available from build %s to %s' % (current, target)
        server_process.terminate()
        server_process = None
        update_server()
        server_process = open_server()

    import time; time.sleep(5)