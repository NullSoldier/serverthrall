from steamfiles import acf
import logging
import os
import shutil
import subprocess


class SteamCmd(object):

    def __init__(self, path):
        super(SteamCmd, self).__init__()
        self.steamcmd_path = path
        self.steamcmd_dir = os.path.dirname(path)
        self.logger = logging.getLogger('serverthrall.steamcmd')

    def _log_steam_cmd(self, command_list):
        self.logger.debug(' '.join(command_list))

    def _build_steamcmd_commands(self, args):
        commands = [self.steamcmd_path] + ["+%s" % c for c in args]
        self._log_steam_cmd(commands)
        return commands

    def _get_steam_output(self, *args):
        commands = self._build_steamcmd_commands(args)
        output = subprocess.check_output(commands, stderr=subprocess.PIPE)
        return output.decode('UTF-8', 'replace')

    def _stream_steam_output(self, *args):
        commands = self._build_steamcmd_commands(args)

        return subprocess.Popen(
            commands,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=200)

    def _execute_steam_commands(self, *args):
        commands = self._build_steamcmd_commands(args)
        self._log_steam_cmd(commands)
        return subprocess.call(commands, stderr=subprocess.STDOUT)

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
            'login anonymous',
            'app_info_update 1',
            'app_info_print %s' % app_id,
            'app_info_print %s' % app_id,
            'quit').splitlines()

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

    def update_app(self, app_id, app_dir, beta=None):
        self.try_delete_cache()

        if beta:
            beta = '-beta ' + beta

        self._execute_steam_commands(
            'login anonymous',
            'force_install_dir "%s"' % app_dir,
            'app_update %s validate %s' % (app_id, beta),
            'quit')

    def update_workshop_item(self, app_id, item_id):
        process = self._stream_steam_output(
            'login anonymous',
            'workshop_download_item %s %s' % (app_id, item_id),
            'quit')

        detect_success = False
        log_buffer = []

        while process.poll() is None:
            out_line = process.stdout.readline().decode('UTF-8', 'replace')
            err_line = process.stderr.readline().decode('UTF-8', 'replace')

            if len(err_line) > 0:
                log_buffer.append(err_line)

            if len(out_line) > 0:
                if 'Success' in out_line:
                    detect_success = True
                self.logger.debug(out_line)
                log_buffer.append(out_line)

        if not detect_success:
            self.logger.error('\n'.join(log_buffer))

        return process.returncode == 0 and detect_success
