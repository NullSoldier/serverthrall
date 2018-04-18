from .intervaltickplugin import IntervalTickPlugin
from serverthrall import settings
from steamfiles import acf
from datetime import datetime
import time
import subprocess
import os


class ServerUpdater(IntervalTickPlugin):

    NO_INSTALLED_VERSION = ''
    NO_INSTALLED_BRANCH = 'public'
    FIFTEEN_MINUTES_IN_SECONDS = 15 * 60

    def __init__(self, config):
        super(ServerUpdater, self).__init__(config)
        config.set_default('interval.interval_seconds', self.FIFTEEN_MINUTES_IN_SECONDS)
        config.set_default('installed_version', self.NO_INSTALLED_VERSION)
        config.set_default('installed_branch', self.NO_INSTALLED_BRANCH)
        config.queue_save()

    def ready(self, steamcmd, server, thrall):
        super(ServerUpdater, self).ready(steamcmd, server, thrall)
        self.installed_version = self.config.get('installed_version')
        self.installed_branch = self.config.get('installed_branch')

        if self.installed_version == self.NO_INSTALLED_VERSION:
            self.detect_existing_version()

        self.logger.info('Auto updater ready, currently known buildid is %s', self.installed_version)

        if self.installed_branch != self.get_config_branch():
            self.tick_early()

    def get_config_branch(self):
        return 'testlive' if self.thrall.config.getboolean('testlive') else 'public'

    def get_current_timestamp(self):
        return time.mktime(datetime.now().timetuple())

    def detect_existing_version(self):
        buildid = self.get_installed_build_id()

        self.installed_version = buildid
        self.config.set('installed_version', buildid)
        self.config.queue_save()

        if buildid != self.NO_INSTALLED_VERSION:
            self.logger.info('Conan server already installed with buildid %s' % buildid)

    def get_installed_build_id(self):
        appmanifest_path = os.path.join(
            self.thrall.config.get_server_root(),
            'steamapps/appmanifest_%s.acf' % settings.CONAN_SERVER_APP_ID)

        if not os.path.exists(appmanifest_path):
            return self.NO_INSTALLED_VERSION

        with open(appmanifest_path, 'r') as f:
            data = acf.load(f)

        return data['AppState']['buildid']

    def get_available_build_id(self, branch=None):
        app_info = None
        try:
            app_info = self.steamcmd.get_app_info(settings.CONAN_SERVER_APP_ID)
        except subprocess.CalledProcessError as ex:
            return None, ex

        build_id = None

        if branch is None:
            # latest build id of any branch
            build_id = max(int(b['buildid']) for b in app_info
                [settings.CONAN_SERVER_APP_ID]
                ['depots']
                ['branches']
                .values())
        else:
            # build id of specific branch
            build_id = (app_info
                [settings.CONAN_SERVER_APP_ID]
                ['depots']
                ['branches']
                [branch]
                ['buildid'])

        return build_id, None

    def is_update_available(self):
        available_build_id, exc = self.get_available_build_id(branch=self.get_config_branch())

        if available_build_id is None:
            error_message = 'Failed to check for update: %s' % exc
            if exc.output:
                error_message += '\n===========\n'
                error_message += exc.output.decode('UTF-8', 'replace')
                error_message += '\n==========='
            self.logger.error(error_message)
            self.tick_early()  # if there is an error, try again
            return False, None, None

        if self.installed_version == self.NO_INSTALLED_VERSION:
            return True, None, available_build_id

        current = int(self.installed_version)
        latest = int(available_build_id)
        is_latest_newer = latest > current

        if self.installed_branch != self.get_config_branch():
            self.logger.info('Client is not using the correct branch, updating to %s', self.get_config_branch())
            is_latest_newer = True

        return is_latest_newer, current, latest

    def update_server(self, target_build_id, target_branch):
        self.server.install_or_update()
        self.installed_version = target_build_id
        self.installed_branch = target_branch
        self.config.set('installed_version', target_build_id)
        self.config.set('installed_branch', target_branch)
        self.config.queue_save()

    def tick_interval(self):
        is_available, current, target = self.is_update_available()

        if is_available:
            self.logger.info('An update is available from build %s to %s' % (current, target))
            self.server.close()
            self.update_server(target, self.get_config_branch())
            self.thrall.conan_config.refresh()
            self.server.start()
