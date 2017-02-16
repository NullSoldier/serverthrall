from .sectionforcedconfig import SectionForcedConfig
from .util import config_save
import os


class ThrallConfig(SectionForcedConfig):

    def __init__(self, config):
        super(ThrallConfig, self).__init__('ServerThrall', config)
        self.set_default('server_version', None)
        self.set_default('conan_server_directory', os.path.join(os.getcwd(), 'vendor\\server'))

    def save(self):
    	config_save(self.config)
