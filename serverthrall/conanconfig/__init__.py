from .conanconfigparser import ConanConfigParser
from .utils import guess_file_encoding
from collections import OrderedDict
import logging
import os
import time

CONAN_SETTINGS_MAPPING = {
    'ServerName':           ('Engine', 'OnlineSubsystem', 'ServerName'),
    'ServerPassword':       ('Engine', 'OnlineSubsystem', 'ServerPassword'),
    'QueryPort':            ('Engine', 'OnlineSubsystemSteam', 'GameServerQueryPort'),
    'NetServerMaxTickRate': ('Engine', '/Script/OnlineSubsystemUtils.IpNetDriver', 'NetServerMaxTickRate'),

    'RconEnabled':  ('Game', 'RconPlugin', 'RconEnabled'),
    'RconPassword': ('Game', 'RconPlugin', 'RconPassword'),
    'RconPort':     ('Game', 'RconPlugin', 'RconPort'),
    'RconMaxKarma': ('Game', 'RconPlugin', 'RconMaxKarma'),
    'MaxPlayers':   ('Game', '/Script/Engine.GameSession', 'MaxPlayers'),

    'AdminPassword':                    ('ServerSettings', 'ServerSettings', 'AdminPassword'),
    'MaxNudity':                        ('ServerSettings', 'ServerSettings', 'MaxNudity'),
    'IsBattlEyeEnabled':                ('ServerSettings', 'ServerSettings', 'IsBattlEyeEnabled'),
    'ServerRegion':                     ('ServerSettings', 'ServerSettings', 'ServerRegion'),
    'ServerCommunity':                  ('ServerSettings', 'ServerSettings', 'ServerCommunity'),
    'PVPEnabled':                       ('ServerSettings', 'ServerSettings', 'PVPEnabled'),
    'BuildingPreloadRadius':            ('ServerSettings', 'ServerSettings', 'BuildingPreloadRadius'),
    'MaxBuildingDecayTime':             ('ServerSettings', 'ServerSettings', 'MaxBuildingDecayTime'),
    'MaxDecayTimeToAutoDemolish':       ('ServerSettings', 'ServerSettings', 'MaxDecayTimeToAutoDemolish'),
    'PlayerOfflineThirstMultiplier':    ('ServerSettings', 'ServerSettings', 'PlayerOfflineThirstMultiplier'),
    'PlayerOfflineHungerMultiplier':    ('ServerSettings', 'ServerSettings', 'PlayerOfflineHungerMultiplier'),
    'LogoutCharactersRemainInTheWorld': ('ServerSettings', 'ServerSettings', 'LogoutCharactersRemainInTheWorld'),

    'KickAFKPercentage': ('ServerSettings', 'ServerSettings', 'KickAFKPercentage'),
    'KickAFKTime':       ('ServerSettings', 'ServerSettings', 'KickAFKTime'),
}

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
                        group_config.write(group_file)

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
