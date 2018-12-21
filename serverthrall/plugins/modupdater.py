from .intervaltickplugin import IntervalTickPlugin
from .restartmanager import RestartManager
from datetime import datetime
from serverthrall import settings
from serverthrall.utils import ProgressBar
from steamfiles import acf
from string import Template
import os
import shutil
import subprocess


class ModUpdater(IntervalTickPlugin):

    MAX_NAME_COUNT = 5
    ONE_HOUR_IN_SECONDS = 1 * 60 * 60

    def __init__(self, config):
        config.set_default('interval.interval_seconds', self.ONE_HOUR_IN_SECONDS)
        config.set_default('workshop_ids', '')
        config.set_default('last_updated', 0)
        super(ModUpdater, self).__init__(config)

    def ready(self, steamcmd, server, thrall):
        super(ModUpdater, self).ready(steamcmd, server, thrall)
        self.restartmanager = self.thrall.get_plugin(RestartManager)
        self.workshop_ids = self.config.getintarray('workshop_ids')
        self.last_updated = self.config.getint('last_updated')
        self.known_mod_names = {}
        self.waiting_for_restart = False

        self.server_mods_dir = os.path.join(
            self.thrall.config.get_server_root(),
            'ConanSandbox',
            'Mods')

        self.server_modlist_path = os.path.join(
            self.server_mods_dir,
            'modlist.txt')

        self.steamcmd_mods_dir = os.path.join(
            self.steamcmd.steamcmd_dir,
            'steamapps',
            'workshop',
            'content',
            '%s' % settings.CONAN_CLIENT_APP_ID)

        self.steamcmd_mod_manifest_path = os.path.join(
            self.steamcmd.steamcmd_dir,
            'steamapps',
            'workshop',
            'appworkshop_%s.acf' % settings.CONAN_CLIENT_APP_ID)

        self.update_known_mod_names()

    def format_mod_names(self, workshop_ids, force_all=False):
        if len(workshop_ids) <= self.MAX_NAME_COUNT or force_all:
            return ', '.join(map(self.get_mod_name, workshop_ids))
        else:
            return '%s and %s more mods' % (
                ', '.join(map(self.get_mod_name, workshop_ids[:self.MAX_NAME_COUNT])),
                len(workshop_ids) - self.MAX_NAME_COUNT)

    def update_known_mod_names(self):
        result = {}
        pakfiles = self.get_downloaded_pakfiles()

        for workshop_id, pakfiles in pakfiles.items():
            if len(pakfiles) > 0:
                result[workshop_id] = pakfiles[0].replace('.pak', '')

        self.known_mod_names = result

    def get_mod_name(self, workshop_id):
        if workshop_id in self.known_mod_names:
            return self.known_mod_names[workshop_id]
        return '#' + str(workshop_id)

    def read_mod_list(self):
        pakfiles = []

        if os.path.exists(self.server_modlist_path):
            with open(self.server_modlist_path, 'r') as f:
                for line in f.readlines():
                    line = line.strip()
                    if len(line) > 0 and line:
                        pakfiles.append(line)

        return pakfiles

    def write_mod_list(self, pakfiles):
        with open(self.server_modlist_path, 'w') as f:
            f.write('\n'.join([p.strip() for p in pakfiles if len(p) > 0]))

    def get_manifest_updated_times(self):
        if not os.path.exists(self.steamcmd_mod_manifest_path):
            self.logger.debug('Doesnt exist: %s' % self.steamcmd_mod_manifest_path)
            return {}

        with open(self.steamcmd_mod_manifest_path, 'r') as f:
            data = acf.load(f)

        mods_updated = {}
        for workshop_id in data['AppWorkshop']['WorkshopItemsInstalled']:
            mod = data['AppWorkshop']['WorkshopItemsInstalled'][workshop_id]
            mods_updated[workshop_id] = int(mod['timeupdated'])
        return mods_updated

    def get_installed_pakfiles(self):
        result = set()

        if os.path.exists(self.server_mods_dir):
            for pakfile in os.listdir(self.server_mods_dir):
                if pakfile.endswith('.pak'):
                    result.add(pakfile)

        return result

    def get_downloaded_pakfiles(self):
        result = dict()

        for workshop_id in self.workshop_ids:
            result[workshop_id] = []

            download_mod_dir = os.path.join(self.steamcmd_mods_dir, str(workshop_id))
            if not os.path.exists(download_mod_dir):
                continue

            for pakfile in os.listdir(download_mod_dir):
                if pakfile.endswith('.pak'):
                    result[workshop_id].append(pakfile)

        return result

    def get_outdated_mods(self):
        result = set()

        # check updated mods that need to be copied
        updated_times = self.get_manifest_updated_times()
        for workshop_id, last_updated in updated_times.items():
            if last_updated > self.last_updated:
                result.add(workshop_id)

        # check for pakfiles that arent in modlist
        # and pakfiles missing from installation
        modlist_pakfiles = self.read_mod_list()
        downloaded_pakfiles = self.get_downloaded_pakfiles()
        installed_pakfiles = self.get_installed_pakfiles()

        for workshop_id, pakfiles in downloaded_pakfiles.items():
            for pakfile in pakfiles:
                if pakfile not in modlist_pakfiles:
                    result.add(workshop_id)
                elif pakfile not in installed_pakfiles:
                    result.add(workshop_id)

        return list(result)

    def sync_mods(self, workshop_ids):
        self.logger.info('Syncing updated mod files for %s' % self.format_mod_names(workshop_ids, True))

        pakfiles = self.read_mod_list()

        # Copy pak files from steamcmd to conan server
        for workshop_id in workshop_ids:
            download_mod_dir = os.path.join(self.steamcmd_mods_dir, '%s' % workshop_id)

            if not os.path.exists(download_mod_dir):
                continue

            for pakfile in os.listdir(download_mod_dir):
                if pakfile.endswith('.pak'):
                    pak_source = os.path.join(download_mod_dir, pakfile)
                    pak_dest = os.path.join(self.server_mods_dir, pakfile)

                    self.logger.debug('Copying PAK file %s\n%s\n%s' % (pakfile, pak_source, pak_dest))
                    shutil.copyfile(pak_source, pak_dest)

                    if pakfile not in pakfiles:
                        pakfiles.append(pakfile)

        # use the preferred mod order before writing out the mod list
        print('OLD MODLIST', pakfiles)
        pakfiles = self.reorder_mod_list(pakfiles)
        print('NEW MODLIST', pakfiles)

        self.write_mod_list(pakfiles)
        self.logger.info('Finished updating mods')

    def reorder_mod_list(self, modlist):
        managed_pakfiles  = self.get_downloaded_pakfiles()

        managed_pakfiles_set = set()
        for pakfile_list in managed_pakfiles.values():
            for pakfile in pakfile_list:
                managed_pakfiles_set.add(pakfile)

        result = []

        for pakfile in modlist:
            if pakfile not in managed_pakfiles_set:
                result.append(result)

        for workshop_id in self.workshop_ids:
            result = result + managed_pakfiles.get(workshop_id, [])

        return result

    def tick_interval(self):
        if len(self.workshop_ids) == 0 or self.waiting_for_restart:
            return

        self.logger.info('Checking for mod updates for %s' % self.format_mod_names(self.workshop_ids))

        outdated_mods = []
        try:
            progress = ProgressBar(lambda c, t, i:
                '%d / %d (Checking %s)' % (c - 1, t, self.get_mod_name(i)))

            for index, workshop_id in enumerate(self.workshop_ids):
                progress.display(self.workshop_ids, index)

                if not self.steamcmd.update_workshop_item(settings.CONAN_CLIENT_APP_ID, workshop_id):
                    progress.clear()
                    self.logger.error('Error while updating %s' % self.get_mod_name(workshop_id))
                    return

            progress.clear()

            self.update_known_mod_names()
            outdated_mods = self.get_outdated_mods()
        except subprocess.CalledProcessError:
            self.logger.error('Failed to check for mod updates')
            return

        if len(outdated_mods) == 0:
            self.logger.info('All mods are already updated.')
            return

        self.logger.info('%d mods are out of date, %s'
            % (len(outdated_mods), self.format_mod_names(outdated_mods, True)))

        def on_notify_offline():
            try:
                self.sync_mods(outdated_mods)
            except:
                self.logger.exception('Failed to sync new mod files, aborting updating mods.')
                return

            self.waiting_for_restart = False
            self.last_updated = int(datetime.utcnow().timestamp())
            self.config.set('last_updated', self.last_updated)

        discord_warning, rcon_warning = self.get_warning_messages(outdated_mods)
        discord_restart, rcon_restart = self.get_restart_messages(outdated_mods)

        self.waiting_for_restart = True
        self.restartmanager.start_restart(
            plugin=self,
            rcon_warning=rcon_warning,
            rcon_restart=rcon_restart,
            discord_warning=discord_warning,
            discord_restart=discord_restart,
            restart_callback=on_notify_offline)

    def get_restart_messages(self, workshop_ids):
        default_message = self.thrall.localization.return_word('ModUpdater.restart')
        discord_message = default_message
        rcon_message = default_message

        if self.config.has_option_filled('discord_restart_message'):
            discord_message = self.config.get('discord_restart_message')

        if self.config.has_option_filled('rcon_restart_message'):
            rcon_message = self.config.get('rcon_restart_message')

        template = {
            'mods': self.format_mod_names(workshop_ids, True),
            'mods_short': self.format_mod_names(workshop_ids),
            'mods_count': len(workshop_ids)
        }

        discord_message = Template(discord_message).safe_substitute(template)
        rcon_message = Template(rcon_message).safe_substitute(template)

        return discord_message, rcon_message

    def get_warning_messages(self, workshop_ids):
        default_message = self.thrall.localization.return_word('ModUpdater.warning')
        discord_message = default_message
        rcon_message = default_message

        if self.config.has_option_filled('discord_warning_message'):
            discord_message = self.config.get('discord_warning_message')

        if self.config.has_option_filled('rcon_warning_message'):
            rcon_message = self.config.get('rcon_warning_message')

        template = {
            'mods': self.format_mod_names(workshop_ids, True),
            'mods_short': self.format_mod_names(workshop_ids),
            'mods_count': len(workshop_ids)
        }

        discord_message = Template(discord_message).safe_substitute(template)
        rcon_message = Template(rcon_message).safe_substitute(template)

        return discord_message, rcon_message
