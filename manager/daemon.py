import subprocess
import time
import psutil
from steamcmd import SteamCmd
from config import load_config, save_config
from datetime import datetime
import ConfigParser
import os


DEFAULT_CONFIG = {
    'build_id': 0,
    'app_id': 443030,
    'raid_timer_enabled': 'True',
    'raid_start_hour': 17,
    'raid_length_hours': 5,
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
        try:
            app_info = self.steamcmd.get_app_info(self.config['app_id'])
        except subprocess.CalledProcessError as ex:
            print 'Failed to check for update %s' % ex
            return False, None, None

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

    def load_raid_enabled(self):
        path = os.path.join(self.config['conan_dir'],
            'ConanSandbox\\Saved\\Config\\WindowsServer\\ServerSettings.ini')

        config = ConfigParser.ConfigParser()
        config.read(path)

        try:
            return config.get('ServerSettings', 'CanDamagePlayerOwnedStructures') == 'True'
        except ConfigParser.NoOptionError:
            return False

    def save_raid_enabled(self, raid_enabled):
        path = os.path.join(self.config['conan_dir'],
            'ConanSandbox\\Saved\\Config\\WindowsServer\\ServerSettings.ini')

        config = ConfigParser.ConfigParser()
        config.read(path)
        config.set('ServerSettings', 'CanDamagePlayerOwnedStructures', raid_enabled)

        with open(path, 'w') as settings_file:
            config.write(settings_file)

    def is_raid_time(self):
        _, _, _, hour, _, _, _, _, _ = datetime.now().timetuple()
        start = int(self.config['raid_start_hour'])
        end = start + int(self.config['raid_length_hours'])
        return start <= hour and hour <= end

    def run(self):
        self.config = load_config()

        if self.config is None:
            print 'No config found, creating new config'
            self.config = DEFAULT_CONFIG
            save_config(self.config)

        self.raid_enabled = self.load_raid_enabled()
        self.steamcmd = SteamCmd(self.config['steamcmd_path'])

        while True:
            is_available, current, target = self.is_update_available()
            is_raid_time = self.is_raid_time()

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

            if self.config['raid_timer_enabled'] == 'True' and self.raid_enabled != is_raid_time:
                print 'Changing raid status from %s to %s' % (self.raid_enabled, is_raid_time)
                self.close_server()
                self.save_raid_enabled(is_raid_time)
                self.raid_enabled = is_raid_time
                self.start_server()

            time.sleep(5)
