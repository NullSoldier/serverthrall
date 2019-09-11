# Credit to https://stackoverflow.com/a/31280850 for help with this
import os
import subprocess
import sys
import tempfile
import traceback

POWERSHELL_TIMEOUT = 30
WAIT_FOR_CLOSE_TIMEOUT = 60 * 2

SCRIPT_TEMPLATE = """
[void] [System.Reflection.Assembly]::LoadWithPartialName("'Microsoft.VisualBasic")
[Microsoft.VisualBasic.Interaction]::AppActivate("{0}")

[void] [System.Reflection.Assembly]::LoadWithPartialName("'System.Windows.Forms")
[System.Windows.Forms.SendKeys]::SendWait("^" + "c")
"""

def get_process_window_titles(pid=None):
    import win32api
    import win32con
    import win32gui
    import win32process

    titles = []

    def enum_windows_process(window_handle, process_pid):
        (other_thread_id, other_process_id) = win32process.GetWindowThreadProcessId(window_handle)

        if other_process_id != process_pid:
            return

        text = win32gui.GetWindowText(window_handle)
        if not text:
            return

        window_style = win32api.GetWindowLong(window_handle, win32con.GWL_STYLE)

        if window_style & win32con.WS_VISIBLE:
            titles.append(text)

    win32gui.EnumWindows(enum_windows_process, pid)
    return titles


def write_and_execute_script_for(window_title):
    rendered_script = SCRIPT_TEMPLATE.format(window_title)

    file = tempfile.NamedTemporaryFile(
        delete=False,
        mode='w',
        encoding='utf8',
        suffix='.ps1')

    try:
        file.write(rendered_script)
        file.close()

        return subprocess.call(
            ['powershell', file.name],
            timeout=POWERSHELL_TIMEOUT,
            stderr=subprocess.STDOUT)
    finally:
        os.remove(file.name)

    return 1

def close_server_windows(conan_server):
    try:
        window_titles = get_process_window_titles(conan_server.process.pid)

        if not window_titles:
            return False

        for window_title in window_titles:
            conan_server.logger.debug('Sending CTRL+C to %s' % window_title)
            result = write_and_execute_script_for(window_title)

            if result != 0:
                return False

        conan_server.logger.debug('Waiting for server to close before %s seconds' % str(WAIT_FOR_CLOSE_TIMEOUT))
        conan_server.wait_for_close(WAIT_FOR_CLOSE_TIMEOUT)
    except Exception:
        exc_type, value, trace = sys.exc_info()
        conan_server.logger.debug('Crash when attempting to shut down server safely')
        conan_server.logger.debug("".join(traceback.format_exception(exc_type, value, trace)))
        return False

    return True
