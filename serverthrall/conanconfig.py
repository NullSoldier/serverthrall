from collections import OrderedDict
from configparser import ConfigParser
from contextlib import contextmanager
import logging
import os


class MultiSetOrderedDict(OrderedDict):

    def __setitem__(self, key, value):
        if key in self:
            item = self.__getitem__(key)

            if isinstance(value, list):
                item.extend(value)
            else:
                item.append(value)
        else:
            super(MultiSetOrderedDict, self).__setitem__(key, value)

    def items(self, *args, **kwargs):
        result = []

        for key, value in super(MultiSetOrderedDict, self).items(*args, **kwargs):
            if isinstance(value, list):
                for subvalue in value:
                    result.append((key, subvalue))

        return result

class ConanConfigParser(ConfigParser):

    def __init__(self, *args, **kwargs):
        kwargs['interpolation'] = None
        kwargs['strict'] = False
        kwargs['dict_type'] = MultiSetOrderedDict
        super(ConanConfigParser, self).__init__(*args, **kwargs)
        self.optionxform = lambda k: k

    def items(self, *args, **kwargs):
        super(ConanConfigParser, self).items(*args, **kwargs)

class ConanConfig(object):

    def __init__(self, conan_server_directory):
        self.dirty = {}
        self.groups = {}
        self.group_paths = {
            'ServerSettings': [
                os.path.join(conan_server_directory, 'ConanSandbox\\Config\\DefaultServerSettings.ini'),
                os.path.join(conan_server_directory, 'ConanSandbox\\Saved\\Config\\\WindowsServer\\ServerSettings.ini')
            ],
            'Engine': [
                os.path.join(conan_server_directory, 'ConanSandbox\\Config\\DefaultEngine.ini'),
                os.path.join(conan_server_directory, 'ConanSandbox\\Saved\\Config\\\WindowsServer\\Engine.ini')
            ],
            'Game': [
                os.path.join(conan_server_directory, 'ConanSandbox\\Config\\DefaultGame.ini'),
                os.path.join(conan_server_directory, 'ConanSandbox\\Saved\\Config\\\WindowsServer\\Game.ini')
            ]
        }

        self.logger = logging.getLogger('serverthrall.conan_config')
        self.refresh()

    def refresh(self):
        groups = {}

        for key, paths in self.group_paths.items():
            groups[key] = []

            for path in paths:
                config = ConanConfigParser()
                files_read = config.read(path)
                groups[key].append(config)

                if len(files_read) == 0:
                    raise Exception('Failed to load config %s' % path)

        self.groups = groups

    def _query_get(self, group, section, option, getter):
        if group not in self.groups:
            raise Exception('no settings group %s' % group)

        for group_config in reversed(self.groups[group]):
            if not group_config.has_section(section):
                continue
            if not group_config.has_option(section, option):
                continue
            return getattr(group_config, getter)(section, option)

        return None

    def get(self, group, section, option):
        return self._query_get(group, section, option, 'get')

    def getfloat(self, group, section, option):
        return self._query_get(group, section, option, 'getfloat')

    def getboolean(self, group, section, option):
        return self._query_get(group, section, option, 'getboolean')

    def set(self, group, section, option, value, first=False):
        if group not in self.groups:
            raise Exception('no settings group %s' % group)

        # we should generally always write to the LAST config in the hierarchy
        # unless the user has specifically asked to be written to the first in
        # the hierarchy like for MaxTickRate which only works in the base config
        index = 0 if first else len(self.groups[group]) - 1

        if group not in self.dirty:
            self.dirty[group] = []

        while len(self.dirty[group]) < index + 1:
            self.dirty[group].append({})

        if section not in self.dirty[group]:
            self.dirty[group][index][section] = {}

        if not self.groups[group][index].has_section(section):
            self.groups[group][index].add_section(section)

        self.dirty[group][index][section][option] = value
        self.groups[group][index].set(section, option, value)

    def setboolean(self, group, section, option, value):
        self.set(group, section, option, 'True' if value else 'False')

    @contextmanager
    def save(self):
        yield
        self.refresh()

        # patch in dirty settings into the freshly loaded config files
        for group_key, groups in self.dirty.items():
            for group_index, sections in enumerate(groups):
                for section_key, section in sections.items():
                    for option_key, value in section.items():
                        if not self.groups[group_key][group_index].has_section(section_key):
                            self.groups[group_key][group_index].add_section(section_key)

                        self.logger.debug('DIRTY: %s %s.%s=%s' % (
                            self.group_paths[group_key][group_index], section_key, option_key, value))

                        self.groups[group_key][group_index].set(section_key, option_key, value)

        # write modified config files out to the last config path in each group
        for group_key, group in self.groups.items():
            for group_index, group_config in enumerate(group):
                with open(self.group_paths[group_key][group_index], 'w') as group_file:
                    group_config.write(group_file)

        self.dirty = {}
