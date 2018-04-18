from .sectionforcedconfig import SectionForcedConfig
from .util import config_save
from serverthrall import settings
import os


class ThrallConfig(SectionForcedConfig):

    def __init__(self, config):
        super(ThrallConfig, self).__init__('ServerThrall', config)
        self.queued_save = False
        self.set_default('conan_server_directory', os.path.join(os.getcwd(), 'vendor\\server'))
        self.set_default('force_update_on_launch', 'false')
        self.set_default('additional_arguments', '')
        self.set_default('multihome', '')
        self.set_default('set_high_priority', 'false')
        self.set_default('testlive', 'false')
        self.queue_save()
        self.save()

    def get_conan_exe_name(self):
        return self.get('conan_exe_name', settings.CONAN_EXE_NAME)

    def get_conan_exe_subpath(self):
        return self.get('conan_exe_subpath', settings.CONAN_EXE_SUBPATH)

    def save(self):
        config_save(self.config)

    def queue_save(self):
        self.queued_save = True

    def save_if_queued(self):
        if self.queued_save:
            self.save()
            self.queued_save = False
