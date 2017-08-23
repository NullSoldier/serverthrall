from .sectionforcedconfig import SectionForcedConfig
from .util import config_save
import os


class ThrallConfig(SectionForcedConfig):

    def __init__(self, config):
        super(ThrallConfig, self).__init__('ServerThrall', config)
        self.queued_save = False
        self.set_default('conan_server_directory', os.path.join(os.getcwd(), 'vendor\\server'))
        self.set_default('force_update_on_launch', 'false')
        self.set_default('additional_arguments', '')
        self.set_default('conan_exe_name', 'ConanSandboxServer.exe')
        self.set_default('set_high_priority', 'false')
        self.queue_save()

    def save(self):
        config_save(self.config)

    def queue_save(self):
        self.queued_save = True

    def save_if_queued(self):
        if self.queued_save:
            self.save()
            self.queued_save = False
