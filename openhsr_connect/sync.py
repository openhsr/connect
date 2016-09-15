import os
import socket
import logging
import json
from yaml import load as yaml_load
import fnmatch
import getpass  # used until password management is implemented

from smb.SMBConnection import SMBConnection

CONFIG_FILE = '../config.example.yaml'

SMB_SERVER_NAME = 'c206.hsr.ch'
SMB_SERVER_IP = socket.gethostbyname(SMB_SERVER_NAME)
SMB_SHARE_NAME = 'skripte'
SMB_CLIENT_NAME = socket.gethostname()
SMB_DOMAIN = 'HSR'
SMB_SERVER_PORT = 445

# Setup logger
logger = logging.getLogger('connect')
# TODO: setup logger in cli
logger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
formatter = logging.Formatter('[%(levelname)s] [%(name)s]  %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


def smb_login():
    # TODO: Get username and password from keyring
    username = input("Username: ")
    password = getpass.getpass()
    connection = SMBConnection(
        username, password, SMB_CLIENT_NAME,
        SMB_SERVER_NAME, domain=SMB_DOMAIN, use_ntlm_v2=False)
    # TODO: Proper exception handling
    assert connection.connect(SMB_SERVER_IP, SMB_SERVER_PORT)
    logger.info('Connection successful!')
    return connection


def read_config():
    # TODO: Read config from sepperate module
    with open(CONFIG_FILE, 'r') as cf:
        config = yaml_load(cf)
    return config['sync']


def load_cache(filename):
    cache = {}
    if os.path.exists(cache_file):
        with open(cache_file, 'r') as fp:
            cache = json.load(fp)
    return cache


def dump_cache(filename, cache):
    with open(filename, 'w') as fp:
        json.dump(cache, fp)


def exclude_file(path, filename, excludes):
    full_name = '/' + path + '/' + filename
    for exclude in excludes:
        if exclude.startswith('/'):
            if full_name.startswith(exclude):
                return True
        elif '/' in exclude:
            if exclude in full_name:
                return True
        elif fnmatch.fnmatch(filename, exclude):
            return True
    return False


def sync_tree(connection, source, destination, rel_path, excludes, cache):
    remote_path = os.path.join(source, rel_path)
    for shared_file in connection.listPath(SMB_SHARE_NAME, remote_path):
        filename = shared_file.filename
        full_remote_path = os.path.join(remote_path, filename)
        full_local_path = os.path.join(destination, rel_path, filename)
        if filename == '.' or filename == '..':
            continue
        elif exclude_file(rel_path, filename, excludes):
            logger.debug('Skipping ignored file: %s' % full_remote_path)
            continue
        elif shared_file.isDirectory:
            if not os.path.exists(full_local_path):
                logger.debug('Creating missing directory %s' % full_local_path)
                os.makedirs(full_local_path)
            
            if filename not in cache:
                cache[filename] = {}
            sync_tree(
                connection, source, destination,
                os.path.join(rel_path, filename), excludes, cache[filename])
        else:
            new_digest = "%s-%s" % (shared_file.file_size,
                                    shared_file.last_write_time)
            if filename in cache and new_digest == cache[filename]:
                logger.debug('File %s has not changed' % full_remote_path)
                continue

            logger.debug('Downloading file %s' % full_remote_path)
            with open(full_local_path, 'wb') as local_file:
                connection.retrieveFile(SMB_SHARE_NAME, full_remote_path, local_file)
                cache[filename] = new_digest
                logger.debug('Downloading of file %s complete!' % full_remote_path)

            # set last write time to that of the remote file
            os.utime(full_local_path,
                    (shared_file.last_access_time, shared_file.last_write_time))


config = read_config()
connection = smb_login()

for name, repository in config['repositories'].items():
    source = repository['remote_dir']
    destination = repository['local_dir']
    if not os.path.exists(destination):
        os.makedirs(destination)
    logger.info('Starting sync: %s -> %s' % (source, destination))
    excludes = config['global_exclude'] + repository['exclude']
    logger.info('The following patterns will be excluded: %s' % (excludes))
    cache_file = '%s/.%s.json' % (destination, name)
    cache = load_cache(cache_file)
    sync_tree(connection, source, destination, '', excludes, cache)
    dump_cache(cache_file, cache)


connection.close()
