from .conanconfigdict import ConanConfigDict
from configparser import RawConfigParser


class ConanConfigParser(RawConfigParser):

    def __init__(self, *args, **kwargs):
        kwargs['allow_no_value'] = True
        kwargs['converters'] = []
        kwargs['dict_type'] = ConanConfigDict
        kwargs['empty_lines_in_values'] = False
        kwargs['interpolation'] = None
        kwargs['strict'] = False

        super(ConanConfigParser, self).__init__(*args, **kwargs)
        self.optionxform = lambda k: k

    def get(self, *args, **kwargs):
        value = super(ConanConfigParser, self).get(*args, **kwargs)
        if isinstance(value, list) and len(value) == 1:
            return value[0]
        return value

    def _join_multiline_values(self):
        pass
