from serverthrall.conanconfig import ConanConfig
import shutil
import os
import filecmp
import pytest


class TestConanConfig(object):

    @pytest.fixture(autouse=True)
    def setup_method(self, tmpdir):
        self.id = 0
        self.fixture_path = './tests/fixtures/default-engine-before.ini'
        self.tmp_dir = tmpdir
        self.tmp_path = self.generate_config()

    def generate_config(self):
        self.id += 1
        path = os.path.join(self.tmp_dir, 'default-engine-before-%s.ini' % self.id)
        shutil.copyfile(self.fixture_path, path)
        return path

    def test_wait_for_configs_to_exist(self):
        config = ConanConfig(self.tmp_dir)
        config.group_paths = {'Test': [self.tmp_path]}
        config.wait_for_configs_to_exist()

    def test_config_no_change(self):
        config = ConanConfig(self.tmp_dir)
        config.group_paths = {'Test': [self.tmp_path]}
        config.refresh()
        config.save()

        filecmp.cmp(self.fixture_path, self.tmp_path, shallow=False)

    def test_duplicate_options(self):
        config = ConanConfig(self.tmp_dir)
        config.group_paths = {'Test': [self.tmp_path]}
        config.refresh()

        paths = config.get('Test', 'Internationalization', 'LocalizationPaths')

        assert len(paths) == 5
        assert paths[0] == '../../../Engine/Content/Localization/Engine'
        assert paths[1] == '../../../../../Projects/ConanSandbox/Branches/Test/UE4/Content/Localization/Exiles_Items'
        assert paths[2] == '../../../../../Projects/ConanSandbox/Branches/Test/UE4/Content/Localization/Exiles_UI'
        assert paths[3] == '../../../../../Projects/ConanSandbox/Branches/Test/UE4/Content/Localization/Exiles_Dialogues'
        assert paths[4] == '../../../../../Projects/ConanSandbox/Branches/Test/UE4/Content/Localization/Exiles_Code'

    def test_sets_last_file(self):
        parent = self.tmp_path
        child = self.generate_config()

        config = ConanConfig(self.tmp_dir)
        config.group_paths = {'Test': [parent, child]}
        config.refresh()

        config.set('Test', 'FOO', 'BAR', 'BAZ')
        config.save()

        config.group_paths = {'Test': [parent]}
        config.refresh()
        assert config.get('Test', 'FOO', 'BAR') == None

        config.group_paths = {'Test': [child]}
        config.refresh()
        assert config.get('Test', 'FOO', 'BAR') == 'BAZ'
