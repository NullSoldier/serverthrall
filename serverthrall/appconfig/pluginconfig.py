from .sectionforcedconfig import SectionForcedConfig


class PluginConfig(SectionForcedConfig):

    def __init__(self, plugin_class, config, thrall_config):
        self.__thrall_config = thrall_config
        super(PluginConfig, self).__init__(plugin_class.__name__, config)

    def queue_save(self):
        self.__thrall_config.queue_save()

    def save_if_queued(self):
        self.__thrall_config.save_if_queued()
