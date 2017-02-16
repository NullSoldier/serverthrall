# class RaidTimeManager(ServerThrallPlugin):

#     def get_raid_setting(self):
#         path = os.path.join(self.config['conan_dir'],
#             'ConanSandbox\\Config\\DefaultServerSettings.ini')

#         config = ConfigParser.ConfigParser()
#         config.optionxform=str
#         config.read(path)

#         try:
#             return config.get('ServerSettings', 'CanDamagePlayerOwnedStructures') == 'True'
#         except ConfigParser.NoOptionError:
#             return None

#     def set_game_setting(self, enabled):
#         path = os.path.join(self.config['conan_dir'],
#             'ConanSandbox\\Config\\DefaultServerSettings.ini')

#         config = ConfigParser.ConfigParser()
#         config.optionxform=str
#         config.read(path)
#         config.set('ServerSettings', 'CanDamagePlayerOwnedStructures', enabled)

#         with open(path, 'w') as settings_file:
#             config.write(settings_file)

#     def is_raid_time(self):
#         _, _, _, hour, _, _, _, _, _ = datetime.now().timetuple()
#         start = int(self.config['raid_start_hour'])
#         end = start + int(self.config['raid_length_hours'])
#         return start <= hour and hour <= end

#     def ready(self):
#         self.enabled = self.get_config('enabled');
#         self.start_hour = self.get_config('start_hour')
#         self.length_hours = self.get_config('length_hours')

#         self.logger.info('Raid mode is currently %s' % ('enabled' if self.enabled else 'disabled'))
#         # if self.raid_enabled is None:
#         #     self.raid_enabled = False
#         #     self.save_raid_enabled(self.raid_enabled)
#         print 'Raid timer is enabled and raid mode is from %s to %s' % (
#                 int(self.config['raid_start_hour']),
#                 int(self.config['raid_start_hour']) + int(self.config['raid_length_hours']))

#     def tick():
#         if not self.enabled:
#             return

#         current = self.get_game_setting()
#         expected = self.is_raid_time()

#         if current != expected:
#             self.logger.info('Changing raid status from %s to %s' % (current, expected))
#             self.server.close()
#             self.set_game_setting()
#             self.server.start()
