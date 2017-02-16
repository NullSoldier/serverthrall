# class ServerUpdater(ServerThrallPlugin):

#     def is_update_available(self):
#         try:
#             app_info = self.steamcmd.get_app_info(self.config['app_id'])
#         except subprocess.CalledProcessError as ex:
#             print 'Failed to check for update %s' % ex
#             return False, None, None

#         current = int(self.config['build_id'])
#         latest = int(app_info['443030']['extended']['depots']['branches']['public']['buildid'])
#         return latest > current, current, latest

#     def update_server(self):
#         self.steamcmd.update_app(
#             self.config['app_id'],
#             self.config['conan_dir'])

#         app_info = self.steamcmd.get_app_info(self.config['app_id'])
#         self.config['build_id'] = app_info['443030']['extended']['depots']['branches']['public']['buildid']
#         save_config(self.config)

#     def tick():
#         is_available, current, target = self.is_update_available()

#         if is_available:
#             print 'An update is available from build %s to %s' % (current, target)
#             self.close_server()
#             self.update_server()
