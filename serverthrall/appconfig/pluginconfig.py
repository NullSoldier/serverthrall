from .sectionforcedconfig import SectionForcedConfig


class PluginConfig(SectionForcedConfig):

    def __init__(self, pluginClass, config):
        super(PluginConfig, self).__init__(pluginClass.__name__, config)
