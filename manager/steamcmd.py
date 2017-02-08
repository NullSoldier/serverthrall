import subprocess
import json
from steamfiles import acf

STEAM_CMD_PATH = "G:\\steamcmd\\steamcmd.exe"
CONAN_PATH = "G:\\conanserver\\"


def _get_steam_output(*args):
    commands = [STEAM_CMD_PATH] + ["+%s" % c for c in args]
    return subprocess.check_output(commands, stderr=subprocess.PIPE);


def _execute_steam_commands(*args):
    commands = [STEAM_CMD_PATH] + ["+%s" % c for c in args]
    return subprocess.check_output(commands, stderr=subprocess.PIPE);


def get_app_info(app_id):
    output = _get_steam_output(
        'login anonymous',
        'force_install_dir "%s"' % CONAN_PATH,
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

    acf_output = output[first_index+1:last_index]
    return acf.loads('\n'.join(acf_output))


def update_app(app_id, app_dir):
    _execute_steam_commands(
        'login anonymous',
        'force_install_dir "%s"' % app_dir,
        'app_update %s' % app_id,
        'quit')