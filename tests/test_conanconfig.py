from serverthrall.conanconfig import ConanConfig
import filecmp
import os
import pytest
import shutil


class TestConanConfig(object):

    @pytest.fixture(autouse=True)
    def setup_method(self, tmpdir):
        self.id = 0
        self.tmp_dir = tmpdir
        self.tmp_path = self.generate_config('default-engine-before.ini')
        self.config = ConanConfig(self.tmp_dir)

    def generate_config(self, from_fixture_name):
        self.id += 1
        config_path = os.path.join(self.tmp_dir, '%s-%s' % (self.id, from_fixture_name))
        fixture_path = './tests/fixtures/%s' % from_fixture_name
        shutil.copyfile(fixture_path, config_path)
        return config_path, fixture_path

    def test_wait_for_configs_to_exist(self):
        path, _ = self.generate_config('default-engine-before.ini')

        self.config.group_paths = {'Test': [path]}
        self.config.wait_for_configs_to_exist()

    def test_config_no_change(self):
        path, original = self.generate_config('default-engine-before.ini')

        self.config.group_paths = {'Test': [path]}
        self.config.refresh()
        self.config.save()

        filecmp.cmp(original, path, shallow=False)

    def test_duplicate_options(self):
        path, _ = self.generate_config('default-engine-before.ini')

        self.config.group_paths = {'Test': [path]}
        self.config.refresh()

        paths = self.config.get('Test', 'Internationalization', 'LocalizationPaths')

        assert len(paths) == 5
        assert paths[0] == '../../../Engine/Content/Localization/Engine'
        assert paths[1] == '../../../../../Projects/ConanSandbox/Branches/Test/UE4/Content/Localization/Exiles_Items'
        assert paths[2] == '../../../../../Projects/ConanSandbox/Branches/Test/UE4/Content/Localization/Exiles_UI'
        assert paths[3] == '../../../../../Projects/ConanSandbox/Branches/Test/UE4/Content/Localization/Exiles_Dialogues'
        assert paths[4] == '../../../../../Projects/ConanSandbox/Branches/Test/UE4/Content/Localization/Exiles_Code'

    def test_sets_last_file(self):
        parent, _ = self.generate_config('default-engine-before.ini')
        child, _ = self.generate_config('default-engine-before.ini')

        self.config.group_paths = {'Test': [parent, child]}
        self.config.refresh()

        self.config.set('Test', 'FOO', 'BAR', 'BAZ')
        self.config.save()

        self.config.group_paths = {'Test': [parent]}
        self.config.refresh()
        assert self.config.get('Test', 'FOO', 'BAR') is None

        self.config.group_paths = {'Test': [child]}
        self.config.refresh()
        assert self.config.get('Test', 'FOO', 'BAR') == 'BAZ'

    def test_boolean(self):
        path, _ = self.generate_config('default-engine-before.ini')

        self.config.group_paths = {'Test': [path]}
        self.config.refresh()

        self.config.set('Test', 'FOO', 'BAR', True)
        self.config.save()
        assert self.config.get('Test', 'FOO', 'BAR') is True

        self.config.set('Test', 'FOO', 'BAR', False)
        self.config.save()
        assert self.config.get('Test', 'FOO', 'BAR') is False

    def test_get_hierarchy(self):
        parent, _ = self.generate_config('port.ini')
        child, _ = self.generate_config('empty.ini')

        self.config.group_paths = {'Test': [parent, child]}
        self.config.refresh()
        assert self.config.get('Test', 'URL', 'Port') == '7777'

    def test_set_hierarchy(self):
        parent, _ = self.generate_config('port.ini')
        child, _ = self.generate_config('empty.ini')

        self.config.group_paths = {'Test': [parent, child]}
        self.config.refresh()

        assert self.config.get('Test', 'URL', 'Port') == '7777'

        self.config.set('Test', 'URL', 'Port', '7778', first=True)
        self.config.set('Test', 'URL', 'Port', '7778')
        self.config.save()
        self.config.refresh()

        filecmp.cmp(parent, child, shallow=False)
