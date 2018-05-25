from .conanconfigparser import ConanConfigParser
from .mapping import CONAN_SETTINGS_MAPPING
from .utils import guess_file_encoding
from collections import OrderedDict
import logging
import os
import time


class ConanConfig(object):

    def __init__(self, conan_server_directory):
        self.dirty = {}
        self.groups = {}
        self.group_paths = {
            'ServerSettings': [
                os.path.join(conan_server_directory, 'ConanSandbox\\Config\\DefaultServerSettings.ini'),
                os.path.join(conan_server_directory, 'ConanSandbox\\Saved\\Config\\WindowsServer\\ServerSettings.ini')
            ],
            'Engine': [
                os.path.join(conan_server_directory, 'ConanSandbox\\Config\\DefaultEngine.ini'),
                os.path.join(conan_server_directory, 'ConanSandbox\\Saved\\Config\\WindowsServer\\Engine.ini')
            ],
            'Game': [
                os.path.join(conan_server_directory, 'ConanSandbox\\Config\\DefaultGame.ini'),
                os.path.join(conan_server_directory, 'ConanSandbox\\Saved\\Config\\WindowsServer\\Game.ini')
            ]
        }

        self.logger = logging.getLogger('serverthrall.conan_config')

    def refresh(self):
        groups = {}

        for key, paths in self.group_paths.items():
            groups[key] = []

            for path in paths:
                encoding = guess_file_encoding(path)
                config = ConanConfigParser()
                files_read = config.read(path, encoding)
                groups[key].append(config)

                if len(files_read) == 0:
                    raise Exception('Failed to load config %s' % path)

        self.groups = groups
        self._patch_dirty()

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

    def get_setting(self, setting):
        return self.get(setting.file, setting.section, setting.option)

    def get_setting_float(self, setting):
        return self.get_float(setting.file, setting.section, setting.option)

    def get_setting_boolean(self, setting):
        return self.get_boolean(setting.file, setting.section, setting.option)

    def set_setting(self, setting, value, first=False):
        return self.set(setting.file, setting.section, setting.option, value, first)

    def get(self, group, section, option):
        return self._query_get(group, section, option, 'get')

    def get_float(self, group, section, option):
        return self._query_get(group, section, option, 'getfloat')

    def get_boolean(self, group, section, option):
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

        if section not in self.dirty[group][index]:
            self.dirty[group][index][section] = {}

        if not self.groups[group][index].has_section(section):
            self.groups[group][index].add_section(section)

        self.dirty[group][index][section][option] = value
        self.groups[group][index].set(section, option, value)

        return self.group_paths[group][index]

    def setboolean(self, group, section, option, value):
        self.set(group, section, option, 'True' if value else 'False')

    def save(self):
        self.refresh()

        # write modified config files out to the last config path in each group
        for group_key, group in self.groups.items():
            for group_index, group_config in enumerate(group):
                is_modified = (
                    group_key in self.dirty and
                    len(self.dirty[group_key]) > group_index and
                    self.dirty[group_key][group_index] != {})

                if is_modified:
                    with open(self.group_paths[group_key][group_index], 'w') as group_file:
                        group_config.write(group_file, space_around_delimiters=False)

        self.dirty = {}

    def _patch_dirty(self):
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

    def wait_for_configs_to_exist(self):
        group_paths = OrderedDict(self.group_paths)

        def get_ready_status():
            for group in group_paths.values():
                for config_path in group:
                    if not os.path.exists(config_path):
                        return (False, config_path,)

            return (True, None)

        last_waiting_on = None
        while True:
            is_ready, waiting_on = get_ready_status()
            if is_ready:
                return
            if waiting_on != last_waiting_on:
                self.logger.warn('Waiting for config to exist %s' % waiting_on)
                last_waiting_on = waiting_on
            time.sleep(3)

    def _debug_config(self, config, needle=None):
        for section in config.sections():
            found = True

            if needle is not None:
                found = False

                for option in config.options(section):
                    if needle in option:
                        found = True
                        break

            if not found:
                continue

            print('[%s]' % section)
            for option in config.options(section):
                if needle in option:
                    print('%s=%s' % (option, config.get(section, option)))
