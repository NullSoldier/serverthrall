class SectionForcedConfig(object):

    def __init__(self, section_name, config):
        self.section_name = section_name
        self.config = config

        if not config.has_section(section_name):
            config.add_section(section_name)

    def get(self, key):
        return self.config.get(self.section_name, key)

    def getfloat(self, key):
        return self.config.getfloat(self.section_name, key)

    def getboolean(self, key):
        return self.config.getboolean(self.section_name, key)

    def getint(self, key):
        return self.config.getint(self.section_name, key)

    def set(self, key, value):
        self.config.set(self.section_name, key, str(value))

    def set_default(self, key, value):
        if not self.config.has_option(self.section_name, key):
            self.config.set(self.section_name, key, str(value))
