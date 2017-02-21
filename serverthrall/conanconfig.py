from collections import defaultdict
import ConfigParser
import os
import logging


class ConanConfig(object):

    def __init__(self, conan_server_directory):
        self.dirty = {}
        self.groups = {}
        self.group_paths = {
            'ServerSettings': [
                os.path.join(conan_server_directory, 'ConanSandbox\\Config\\DefaultServerSettings.ini'),
                os.path.join(conan_server_directory, 'ConanSandbox\\Saved\\Config\\\WindowsServer\\ServerSettings.ini')
            ]
        }

        self.logger = logging.getLogger('serverthrall.conan_config')
        self.refresh()

    def refresh(self):
        groups = {}

        for key, paths in self.group_paths.iteritems():
            config = ConfigParser.RawConfigParser()
            config.optionxform = str
            files_read = config.read(paths)
            groups[key] = config

            if len(files_read) < len(paths):
                self.logger.warning('WARNING: did not load some settings files for %s' % key)

            if len(files_read) == 0:
                raise Exception('Failed to load group %s, no config files loade')

        self.groups = groups

    def get(self, group, section, option):
        return self.groups[group].get(section, option)

    def getfloat(self, group, section, option):
        return self.groups[group].getfloat(section, option)

    def getboolean(self, group, section, option):
        return self.groups[group].getboolean(section, option)

    def set(self, group, section, option, value):
        if group not in self.dirty:
            self.dirty[group] = {}
        if section not in self.dirty[group]:
            self.dirty[group][section] = {}

        self.dirty[group][section][option] = value
        self.groups[group].set(section, option, value)

    def setboolean(self, group, section, option, value):
        self.set(group, section, option, 'True' if value else 'False')

    def save(self):
        self.refresh()

        # patch in dirty settings into the freshly loaded config files
        for group_key, group in self.dirty.iteritems():
            for section_key, section in group.iteritems():
                for option_key, option in section.iteritems():
                    self.logger.debug('DIRTY: %s.%s.%s=%s' % (group_key, section_key, option_key, option))
                    self.groups[group_key].set(section_key, option_key, option)

        # write modified config files out to the first config path in each group
        for group_key, group in self.groups.iteritems():
            with open(self.group_paths[group_key][0], 'w') as group_file:
                group.write(group_file)
