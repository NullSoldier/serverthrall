from .thrallplugin import ThrallPlugin
from serverthrall import settings
import subprocess


class ServerUpdater(ThrallPlugin):

    def __init__(self, config):
        super(ServerUpdater, self).__init__(config)
        self.config.set_default('installed_version', '')

    def ready(self, steamcmd, server):
        super(ServerUpdater, self).ready(steamcmd, server)
        self.installed_version = self.config.get('installed_version')
        self.logger.info('Autoupdater running, currently known buildid is %s', self.installed_version)

    def get_available_build_id(self):
        app_info = None
        try:
            app_info = self.steamcmd.get_app_info(settings.CONAN_APP_ID)
        except subprocess.CalledProcessError as ex:
            return None, ex

        build_id = (app_info
            [settings.CONAN_APP_ID]
            ['depots']
            ['branches']
            [settings.RELEASE_BRANCH]
            ['buildid'])

        return build_id, None

    def is_update_available(self):
        available_build_id, exc = self.get_available_build_id()

        if available_build_id is None:
            self.logger.error('Failed to check for update: %s' % exc)
            return False, None, None

        if len(self.installed_version.strip()) == 0:
            return True, None, available_build_id

        current = int(self.installed_version)
        latest = int(available_build_id)
        return latest > current, current, latest

    def update_server(self, target_build_id):
        self.server.install_or_update()
        self.installed_version = target_build_id
        self.config.set('installed_version', target_build_id)

    def tick(self):
        is_available, current, target = self.is_update_available()

        if is_available:
            self.logger.info('An update is available from build %s to %s' % (current, target))
            self.server.close()
            self.update_server(target)
            self.server.start()
