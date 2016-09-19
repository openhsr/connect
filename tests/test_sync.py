import pytest
import os
import string
import random
from openhsr_connect import sync, configuration

TEST_FOLDER = 'sync-test'


def remove_smb_tree(share, connection, path):
    for shared_file in connection.listPath(share, path):
        if (shared_file.filename != '.' and shared_file.filename != '..'):
            full_path = os.path.join(path, shared_file.filename)
            if shared_file.isDirectory:
                remove_smb_tree(share, connection, full_path)
            else:
                connection.deleteFiles(share, full_path)

    connection.deleteDirectory(share, path)


def generate_files(n):
    num = 1
    while num <= n:
        filename = "file%s.txt" % num
        random_data = "".join(
            [random.choice(string.ascii_letters) for i in range(random.randrange(10, 5000))])
        with open(filename, 'w') as fp:
            fp.write(random_data)
            fp.write('\noriginal content\n')
        yield filename
        num += 1


def create_remote_structure(connection):
    connection.createDirectory('scratch', 'sync-test/dir1')
    connection.createDirectory('scratch', 'sync-test/dir2')
    connection.createDirectory('scratch', 'sync-test/dir3')
    for n in range(1, 4):
        for filename in generate_files(n):
            file = open(filename, 'rb')
            path = 'sync-test/dir%s/%s' % (n, filename)
            connection.storeFile('scratch', path, file)
            os.remove(filename)


@pytest.fixture
def connection(config):
    connection = sync.smb_login(config)
    connection.createDirectory('scratch', TEST_FOLDER)
    yield connection
    # tear down
    remove_smb_tree('scratch', connection, 'sync-test')
    connection.close()


@pytest.fixture
def config():
    config = configuration.load_config(True)
    # overwrite repositories
    config['sync']['repositories'] = {
        'test': {
            'local-dir': TEST_FOLDER,
            'remote-dir': 'sync-test',
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


def test_sync(config, connection, monkeypatch):
    create_remote_structure(connection)
    monkeypatch.setattr(sync, 'SMB_SHARE_NAME', 'scratch')
    sync.sync(config)
    assert_file_structure('test', TEST_FOLDER)
    sync.remove_tree(TEST_FOLDER)
