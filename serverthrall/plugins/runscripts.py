from .discord import Discord
from .restartmanager import RestartManager
from .thrallplugin import ThrallPlugin
import subprocess
import sys
import traceback


class RunScripts(ThrallPlugin):

    def __init__(self, config):
        config.set_default('enabled', 'false')
        super(RunScripts, self).__init__(config)
        config.set_default('force_run_on_launch', False)
        config.queue_save()

    def ready(self, steamcmd, server, thrall):
        super(RunScripts, self).ready(steamcmd, server, thrall)
        self.discord = thrall.get_plugin(Discord)
        self.restartmanager = self.thrall.get_plugin(RestartManager)
        self.restartmanager.register_offline_callback(self, self.run_script)

        if self.config.getboolean('force_run_on_launch'):
            self.config.set('force_run_on_launch', False)
            self.config.queue_save()
            self.run_script()

    def run_script(self):
        command = self.config.get('command', default='').strip()
        arguments = self.config.get('command_arguments', default=None)
        timeout = self.config.getint('command_timeout', default=None)

        if not command:
            self.logger.warning('You have not provided a command to run')
            return

        process_args = [command]

        if arguments:
            process_args = process_args + [arguments]

        output = ''
        returncode = 0
        failure_message = None

        try:
            output = subprocess.check_output(
                process_args,
                stderr=subprocess.STDOUT,
                shell=True,
                timeout=timeout,
                encoding='utf-8')
        except subprocess.TimeoutExpired as ex:
            returncode = 1
            output = ex.output
            failure_message = 'timed out after %s seconds' % timeout
        except subprocess.CalledProcessError as ex:
            returncode = ex.returncode
            output = ex.output
            failure_message = 'failed with code %s' % returncode
        except Exception as ex:
            returncode = 1
            exc_type, value, trace = sys.exc_info()
            output = "".join(traceback.format_exception(exc_type, value, trace))
            failure_message = 'crashed unexpectedly'

        if output:
            output.strip()

        if returncode != 0:
            message = '%s %s' % (command, failure_message)
            if output:
                message += '\n\n' + output
            self.logger.error(message)
            self.discord.send_message('RunScripts', message)
            return

        self.logger.debug(output)
        self.discord.send_message('RunScripts', output)

    def tick(self):
        pass
