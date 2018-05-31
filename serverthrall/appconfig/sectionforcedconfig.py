import configparser
from ..utils import parse_csv_times


def enable_default(fn):
    no_value = {}

    def wrapper(self, key, *args, **kwargs):
        default = kwargs.pop('default', no_value)
        if len(args) > 0:
            default = args[0]

        try:
            return fn(self, key=key)
        except configparser.NoOptionError as ex:
            if default is no_value:
                raise ex from None
            return default

    return wrapper


class SectionForcedConfig(object):

    def __init__(self, section_name, config):
        self.section_name = section_name
        self.config = config

        if not config.has_section(section_name):
            config.add_section(section_name)

    @enable_default
    def get(self, key):
        return self.config.get(self.section_name, key)

    @enable_default
    def getfloat(self, key):
        return self.config.getfloat(self.section_name, key)

    @enable_default
    def getboolean(self, key):
        return self.config.getboolean(self.section_name, key)

    @enable_default
    def getint(self, key):
        return self.config.getint(self.section_name, key)

    def gettimearray(self, key):
        return parse_csv_times(self.get(key))

    def getintarray(self, key):
        return [int(v.strip()) for v in self.get(key).split(',') if v.strip()]

    def remove_option(self, key):
        self.config.remove_option(self.section_name, key)

    def set(self, key, value):
        self.config.set(self.section_name, key, str(value))

    def set_default(self, key, value):
        if not self.config.has_option(self.section_name, key):
            self.config.set(self.section_name, key, str(value))

    def options(self):
        return self.config.options(self.section_name)

    def has_option(self, key):
        return self.config.has_option(self.section_name, key)

    def has_option_filled(self, key):
        if not self.config.has_option(self.section_name, key):
            return False

        if len(self.get(key).strip()) == 0:
            return False

        return True
