import subprocess
import logging
import acf
import os
import shutil


class SteamCmd(object):

    def __init__(self, path):
        super(SteamCmd, self).__init__()
        self.steamcmd_path = path
        self.steamcmd_dir = os.path.dirname(path)
        self.logger = logging.getLogger('serverthrall.steamcmd')

    def _log_steam_cmd(self, command_list):
        self.logger.debug(' '.join(command_list))

    def _get_steam_output(self, *args):
        commands = [self.steamcmd_path] + ["+%s" % c for c in args]
        self._log_steam_cmd(commands)
        return subprocess.check_output(commands, shell=True, stderr=subprocess.PIPE)

    def _execute_steam_commands(self, *args):
        commands = [self.steamcmd_path] + ["+%s" % c for c in args]
        self._log_steam_cmd(commands)
        return subprocess.call(commands, shell=True, stderr=subprocess.STDOUT)

    def try_delete_cache(self):
        appcache_path = os.path.join(self.steamcmd_dir, 'appcache')
        if os.path.exists(appcache_path):
            shutil.rmtree(appcache_path, True)

        is_success = not os.path.exists(appcache_path)
        if not is_success:
            self.logger.warning('Failed to delete appcache at %s' % appcache_path)

        return is_success

    def get_app_info(self, app_id):
        self.try_delete_cache()

        output = self._get_steam_output(
            '@sSteamCmdForcePlatformType windows',
            'login anonymous',
            'app_info_update 1',
            'app_info_print %s' % app_id,
            'app_info_print %s' % app_id,
            'quit').split('\n')

        first_index = None
        last_index = None

        for index, line in enumerate(output):
            if 'AppID : %s' % app_id in line:
                if first_index is None:
                    first_index = index
                    continue
                else:
                    last_index = index
                    break

        if first_index is None or last_index is None:
            raise Exception('couldnt parse steamcmd app_info output')

        acf_output = output[first_index + 1:last_index]
        return acf.loads('\n'.join(acf_output))

    def update_app(self, app_id, app_dir):
        self.try_delete_cache()

        self._execute_steam_commands(
            '@sSteamCmdForcePlatformType windows',
            'login anonymous',
            'force_install_dir "%s"' % app_dir,
            'app_update %s validate' % app_id,
            'quit')
