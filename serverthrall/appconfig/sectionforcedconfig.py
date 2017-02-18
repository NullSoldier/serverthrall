class SectionForcedConfig(object):

    def __init__(self, section_name, config):
        self.section_name = section_name
        self.config = config

        if not config.has_section(section_name):
            config.add_section(section_name)

    def get(self, key):
        # print 'Get %s.%s' % (self.section_name, key)
        return self.config.get(self.section_name, key)

    def getfloat(self, key):
        # print 'GetFloat %s.%s' % (self.section_name, key)
        return self.config.getfloat(self.section_name, key)

    def getboolean(self, key):
        # print 'GetBoolean %s.%s' % (self.section_name, key)
        return self.config.getboolean(self.section_name, key)

    def set(self, key, value):
        # print 'Set %s.%s=%s' % (self.section_name, key, value)
        self.config.set(self.section_name, key, value)

    def set_default(self, key, value):
        if not self.config.has_option(self.section_name, key):
            # print 'Def %s.%s=%s' % (self.section_name, key, value)
            self.config.set(self.section_name, key, value)
