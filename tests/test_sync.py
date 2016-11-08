import pytest
import os
import string
import random
import builtins
from openhsr_connect import sync, configuration

TEST_FOLDER = 'sync-test'


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
    connection.createDirectory('scratch', os.path.join(TEST_FOLDER, 'dir1'))
    connection.createDirectory('scratch', os.path.join(TEST_FOLDER, 'dir2'))
    connection.createDirectory('scratch', os.path.join(TEST_FOLDER, 'dir3'))
    for n in range(1, 4):
        for filename in generate_files(n, 'original content'):
            with open(filename, 'rb') as file:
                path = '%s/dir%s/%s' % (TEST_FOLDER, n, filename)
                connection.storeFile('scratch', path, file)
            os.remove(filename)


@pytest.fixture
def connection(config):
    new_connection = sync.smb_login(config)
    new_connection.createDirectory('scratch', TEST_FOLDER)
    yield new_connection
    # tear down
    remove_smb_tree('scratch', new_connection, TEST_FOLDER)
    sync.remove_tree(TEST_FOLDER)
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


def assert_file_structure(repo_name, path):
    assert os.path.exists(path)
    assert os.path.exists(os.path.join(path, ".%s.json" % repo_name))
    assert os.path.exists(os.path.join(path, 'dir1'))
    assert os.path.exists(os.path.join(path, 'dir2'))
    assert os.path.exists(os.path.join(path, 'dir3'))
    assert os.path.exists(os.path.join(path, 'dir1', 'file1.txt'))
    assert os.path.exists(os.path.join(path, 'dir2', 'file1.txt'))
    assert os.path.exists(os.path.join(path, 'dir2', 'file2.txt'))
    assert os.path.exists(os.path.join(path, 'dir3', 'file1.txt'))
    assert os.path.exists(os.path.join(path, 'dir3', 'file2.txt'))
    assert os.path.exists(os.path.join(path, 'dir3', 'file3.txt'))


def assert_file_content(filename, test_string):
    data = None
    with open(filename, 'r') as fp:
        data = fp.read()
    assert data.endswith(test_string)


def test_sync_basic(config, connection, monkeypatch):
    create_remote_structure(connection)
    monkeypatch.setattr(sync, 'SMB_SHARE_NAME', 'scratch')
    sync.sync(config)
    assert_file_structure('test', TEST_FOLDER)


def test_local_changes_ask_yes(config, connection, monkeypatch):
    config['sync']['conflict-handling']['local-changes'] = 'ask'
    create_remote_structure(connection)
    monkeypatch.setattr(sync, 'SMB_SHARE_NAME', 'scratch')
    sync.sync(config)
    assert_file_structure('test', TEST_FOLDER)
    # change local file
    with open(os.path.join(TEST_FOLDER, 'dir1/file1.txt'), 'a') as fp:
        fp.write('local change')
    # nothing has changed on the remote, therefore there should not be a prompt here
    sync.sync(config)
    # Change remote file
    for filename in generate_files(1, 'remote change'):
        with open(filename, 'rb') as file:
            path = '%s/dir%s/%s' % (TEST_FOLDER, 1, filename)
            connection.storeFile('scratch', path, file)

    # Now it should ask
    monkeypatch.setattr(builtins, 'input', lambda x: "y")  # answer 'yes'
    sync.sync(config)
    assert_file_content(os.path.join(TEST_FOLDER, 'dir1/file1.txt'), 'remote change')


def test_remote_deleted_ask_yes(config, connection, monkeypatch):
    config['sync']['conflict-handling']['remote-deleted'] = 'ask'
    create_remote_structure(connection)
    monkeypatch.setattr(sync, 'SMB_SHARE_NAME', 'scratch')
    sync.sync(config)
    assert_file_structure('test', TEST_FOLDER)

    remove_smb_tree('scratch', connection, os.path.join(TEST_FOLDER, 'dir1'))
    remove_smb_tree('scratch', connection, os.path.join(TEST_FOLDER, 'dir2'))
    monkeypatch.setattr(builtins, 'input', lambda x: "y")  # answer 'yes'
    sync.sync(config)

    assert not os.path.exists(os.path.join(TEST_FOLDER, 'dir1'))
    assert not os.path.exists(os.path.join(TEST_FOLDER, 'dir2'))
