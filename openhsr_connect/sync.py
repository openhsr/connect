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


def file_differs(filepath, remote_digest):
    local_digest = "%s-%s" % (
        os.path.getsize(filepath), os.path.getmtime(filepath))
    return not remote_digest == local_digest


def ask_for_overwrite(path):
    while True:
        choice = input(
            "Do you want to overwrite %s with the new version? (y/N)" % path)
        choice = choice.lower()
        if choice == '' or choice == 'n':
            return False
        elif choice == 'y':
            return True


def remove_tree(filepath):
    if os.path.isfile(filepath):
        os.remove(filepath)
    else:
        for subfile in os.listdir(filepath):
            remove_tree(subfile)


def sync_tree(connection, source, destination, rel_path, excludes, cache):
    fileset = set(cache)
    remote_path = os.path.join(source, rel_path)
    for shared_file in connection.listPath(SMB_SHARE_NAME, remote_path):
        filename = shared_file.filename
        fileset.discard(filename)
        relative_remote_path = os.path.join(rel_path, filename)
        full_local_path = os.path.join(destination, rel_path, filename)
        if filename == '.' or filename == '..':
            continue
        elif exclude_file(rel_path, filename, excludes):
            logger.debug('Skipping ignored file: %s' % relative_remote_path)
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
            remote_digest = "%s-%s" % (shared_file.file_size,
                                    shared_file.last_write_time)
            if os.path.exists(full_local_path) and filename in cache:
                if remote_digest == cache[filename]:
                    logger.debug('File %s has not changed' % relative_remote_path)
                    continue
                if file_differs(full_local_path, cache[filename]):
                    # file changed locally
                    logger.debug('File %s has changed locally' % relative_remote_path)
                    conflict_handling = config['conflict_handling']['local_changes']
                    if conflict_handling == 'keep':
                        continue
                    elif conflict_handling == 'ask':
                        if not ask_for_overwrite(relative_remote_path):
                            continue
                    elif conflict_handling == 'overwrite':
                        logger.info("File %s will be overwritten" % relative_remote_path)
                    elif conflict_handling == 'makeCopy':
                        # TODO: Create conflict file
                        pass
            
            full_remote_path = os.path.join(remote_path, filename)
            logger.debug('Downloading file %s' % full_remote_path)
            with open(full_local_path, 'wb') as local_file:
                connection.retrieveFile(SMB_SHARE_NAME, full_remote_path, local_file)
                cache[filename] = remote_digest
                logger.debug('Downloading of file %s complete!' % full_remote_path)

            # set last write time to that of the remote file
            os.utime(full_local_path,
                    (shared_file.last_access_time, shared_file.last_write_time))

    if fileset:  # if fileset not empty, remote files have been deleted
        for filename in fileset:
            del cache[filename]
            full_path = os.path.join(destination, rel_path, filename)
            logger.debug('File %s has been deleted on remote' % filename)
            # TODO: Ask Option
            if config['conflict_handling']['remote-deleted'] == 'delete':
                logger.debug('File %s will be removed' % filename)
                remove_tree(full_path)


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
