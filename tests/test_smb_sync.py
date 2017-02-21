import pytest
import os
import string
import random
import builtins
import shutil
from openhsr_connect import smb_sync, configuration

TEST_FOLDER = 'sync-test'
TEST_SHARE = 'scratch'
DEFAULT_CONTENT = 'original content'


def remove_smb_tree(share, connection, path):
    for shared_file in connection.listPath(share, path):
        if shared_file.filename != '.' and shared_file.filename != '..':
            full_path = os.path.join(path, shared_file.filename)
            if shared_file.isDirectory:
                remove_smb_tree(share, connection, full_path)
            else:
                connection.deleteFiles(share, full_path)

    connection.deleteDirectory(share, path)


def generate_files(n, content):
    num = 1
    while num <= n:
        filename = "file%s.txt" % num
        random_data = "".join(
            [random.choice(string.ascii_letters) for i in range(random.randrange(10, 5000))])
        with open(filename, 'w') as fp:
            fp.write(random_data)
            fp.write(content)
        yield filename
        num += 1


def create_remote_structure(connection):
    connection.createDirectory(TEST_SHARE, os.path.join(TEST_FOLDER, 'dir1'))
    connection.createDirectory(TEST_SHARE, os.path.join(TEST_FOLDER, 'dir2'))
    connection.createDirectory(TEST_SHARE, os.path.join(TEST_FOLDER, 'dir3'))
    for n in range(1, 4):
        for filename in generate_files(n, DEFAULT_CONTENT):
            with open(filename, 'rb') as file:
                path = '%s/dir%s/%s' % (TEST_FOLDER, n, filename)
                connection.storeFile(TEST_SHARE, path, file)
            os.remove(filename)


@pytest.fixture
def create_smb_sync(config):
    return smb_sync.SMB_Sync(config)


@pytest.fixture
def connection(config, create_smb_sync, monkeypatch):
    monkeypatch.setattr(smb_sync.SMB_Sync, 'SMB_SHARE_NAME', TEST_SHARE)
    new_connection = create_smb_sync.connect()
    new_connection.createDirectory(TEST_SHARE, TEST_FOLDER)
    yield new_connection
    # tear down
    remove_smb_tree(TEST_SHARE, new_connection, TEST_FOLDER)
    shutil.rmtree(TEST_FOLDER)
    new_connection.close()


@pytest.fixture
def config():
    config = configuration.load_config(True)
    # overwrite repositories
    config['sync']['repositories'] = {
        'test': {
            'local-dir': TEST_FOLDER,
            'remote-dir': TEST_FOLDER,
            'exclude': []
        }
    }
    return config


def assert_local_file_structure():
    repo_name = 'test'
    assert os.path.exists(TEST_FOLDER)
    assert os.path.exists(os.path.join(TEST_FOLDER, ".%s.json" % repo_name))
    assert os.path.exists(os.path.join(TEST_FOLDER, 'dir1'))
    assert os.path.exists(os.path.join(TEST_FOLDER, 'dir2'))
    assert os.path.exists(os.path.join(TEST_FOLDER, 'dir3'))
    assert os.path.exists(os.path.join(TEST_FOLDER, 'dir1', 'file1.txt'))
    assert os.path.exists(os.path.join(TEST_FOLDER, 'dir2', 'file1.txt'))
    assert os.path.exists(os.path.join(TEST_FOLDER, 'dir2', 'file2.txt'))
    assert os.path.exists(os.path.join(TEST_FOLDER, 'dir3', 'file1.txt'))
    assert os.path.exists(os.path.join(TEST_FOLDER, 'dir3', 'file2.txt'))
    assert os.path.exists(os.path.join(TEST_FOLDER, 'dir3', 'file3.txt'))


def assert_file_content(filename, test_string):
    data = None
    with open(filename, 'r') as fp:
        data = fp.read()
    assert data.endswith(test_string)


def check_basic_sync(config, connection):
    syncer = create_smb_sync(config)
    create_remote_structure(connection)
    syncer.sync()
    assert_local_file_structure()


# ------- Pytest Test Methods ------- #


def test_sync_basic(config, connection):
    check_basic_sync(config, connection)


@pytest.mark.parametrize('conflict_handling, answer', [
    ('ask', 'y'),
    ('ask', 'n'),
    ('overwrite', None),
    ('keep', None),
    ('makeCopy', None),
])
def test_local_changes(config, connection, monkeypatch, conflict_handling, answer):
    TEST_STR_REMOTE = 'remote change'
    TEST_STR_LOCAL = 'local change'
    config['sync']['conflict-handling']['local-changes'] = conflict_handling
    check_basic_sync(config, connection)

    # change local file
    with open(os.path.join(TEST_FOLDER, 'dir1', 'file1.txt'), 'a') as fp:
        fp.write(TEST_STR_LOCAL)
    # nothing has changed on the remote yet, so nothing should change
    syncer = create_smb_sync(config)
    syncer.sync()
    assert_local_file_structure()
    # Change remote file
    for filename in generate_files(1, TEST_STR_REMOTE):
        with open(filename, 'rb') as file:
            path = os.path.join(TEST_FOLDER, 'dir1', filename)
            connection.storeFile(TEST_SHARE, path, file)

    if conflict_handling == 'ask':
        monkeypatch.setattr(builtins, 'input', lambda x: answer)
    syncer = create_smb_sync(config)
    syncer.sync()
    if conflict_handling == 'keep' or answer == 'n':
        expected_content = TEST_STR_LOCAL
    elif conflict_handling in ['overwrite', 'makeCopy'] or answer == 'y':
        expected_content = TEST_STR_REMOTE
    file1_path = os.path.join(TEST_FOLDER, 'dir1', 'file1.txt')
    assert_file_content(file1_path, expected_content)

    if conflict_handling == 'makeCopy':
        expected_name_path = syncer.get_copy_filename(file1_path)
        assert os.path.exists(expected_name_path)
        assert_file_content(expected_name_path, TEST_STR_LOCAL)


@pytest.mark.parametrize('conflict_handling, answer', [
    ('ask', 'y'),
    ('ask', 'n'),
    ('delete', None),
    ('keep', None),
])
def test_remote_deleted(config, connection, monkeypatch, conflict_handling, answer):
    config['sync']['conflict-handling']['remote-deleted'] = conflict_handling
    check_basic_sync(config, connection)

    remove_smb_tree(TEST_SHARE, connection, os.path.join(TEST_FOLDER, 'dir1'))
    connection.deleteFiles(TEST_SHARE, os.path.join(TEST_FOLDER, 'dir2', 'file1.txt'))

    if conflict_handling == 'ask':
        monkeypatch.setattr(builtins, 'input', lambda x: answer)
    syncer = create_smb_sync(config)
    syncer.sync()

    if conflict_handling == 'keep' or answer == 'n':
        assert_local_file_structure()
    elif conflict_handling == 'delete' or answer == 'y':
        assert not os.path.exists(os.path.join(TEST_FOLDER, 'dir1'))
        assert not os.path.exists(os.path.join(TEST_FOLDER, 'dir2', 'file1.txt'))
        assert os.path.exists(os.path.join(TEST_FOLDER, 'dir2', 'file2.txt'))


@pytest.mark.parametrize('conflict_handling, expected_content', [
    ('keep', 'existing file'),
    ('overwrite', 'default content'),
])
def test_existing_local_files(config, connection, conflict_handling, expected_content):
    config['sync']['conflict-handling']['local-changes'] = conflict_handling
    dirname = os.path.join(TEST_FOLDER, 'dir1')
    os.makedirs(dirname)
    for filename in generate_files(2, 'existing file'):
        os.rename(filename, os.path.join(dirname, filename))
    check_basic_sync(config, connection)

    assert_file_content(os.path.join(TEST_FOLDER, 'dir1', 'file1.txt'), expected_content)

    # on a second sync, no question should be asked
    config['sync']['conflict-handling']['local-changes'] = 'ask'
    syncer = create_smb_sync(config)
    syncer.sync()
    assert_local_file_structure()
    assert_file_content(os.path.join(TEST_FOLDER, 'dir1', 'file1.txt'), expected_content)
