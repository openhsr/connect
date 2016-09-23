import os
from datetime import datetime
import socket
import logging
import json
import fnmatch
from . import configuration
from . import exceptions

from smb.SMBConnection import SMBConnection
from smb.smb_structs import ProtocolError


SMB_SERVER_NAME = 'c206.hsr.ch'
SMB_SHARE_NAME = 'skripte'
SMB_DOMAIN = 'HSR'
SMB_SERVER_PORT = 445

logger = logging.getLogger('openhsr_connect.sync')


def smb_login(config):
    username = config['login']['username']
    password = configuration.get_password(config)
    try:
        server_ip = socket.gethostbyname(SMB_SERVER_NAME)
    except OSError as e:
        logger.debug("Exception when connecting to %s: %s" % (SMB_SERVER_NAME, e))
        raise exceptions.ConnectException(
            'Could not find %s, are you in the HSR network?' % SMB_SERVER_NAME)

    client_name = socket.gethostname()
    connection = SMBConnection(
        username, password, client_name,
        SMB_SERVER_NAME, domain=SMB_DOMAIN, use_ntlm_v2=False)
    try:
        connect_result = connection.connect(server_ip, SMB_SERVER_PORT)
        if connect_result is False:
            raise ProtocolError("SMB Connection failure")
    except ProtocolError as e:
        logger.debug("Exception when connecting to %s: %s" % (SMB_SERVER_NAME, e))
        raise exceptions.ConnectException(
            "Connection to %s failed, wrong password?" % SMB_SERVER_NAME)
    logger.debug('SMB Connection to %s successful!' % SMB_SERVER_NAME)
    return connection


def load_cache(filename):
    cache = {}
    if os.path.exists(filename):
        with open(filename, 'r') as fp:
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


def handle_local_change(full_local_path, rel_remote_path, config):
    logger.debug('File %s has changed locally' % rel_remote_path)
    handling_config = config['local-changes']
    if handling_config == 'keep':
        return 'keep'
    elif handling_config == 'ask':
        question = "Do you want to overwrite %s with the new version?"
        if not ask_question(question % full_local_path):
            return 'keep'
        logger.debug("File %s will be overwritten" % full_local_path)
    elif handling_config == 'overwrite':
        logger.info("File %s will be overwritten" % full_local_path)
    elif handling_config == 'makeCopy':
        rename_file(full_local_path)


def ask_question(question):
    while True:
        choice = input("%s (y/N)" % question)
        choice = choice.lower()
        if choice == '' or choice == 'n':
            return False
        elif choice == 'y':
            return True


def download_file(connection, remote, local):
    logger.info('Downloading file %s' % remote)
    with open(local, 'wb') as local_file:
        connection.retrieveFile(SMB_SHARE_NAME, remote, local_file)
        logger.debug('Downloading of file %s complete!' % remote)


def rename_file(path):
    date = datetime.now().strftime("%y%m%d%H%M")
    filename, extension = os.path.splitext(path)
    new_path = "%s-local-%s%s" % (filename, date, extension)
    logger.debug("Rename local file %s to %s" % (path, new_path))
    os.rename(path, new_path)


def remove_tree(filepath):
    if os.path.isfile(filepath):
        os.remove(filepath)
    else:
        for subfile in os.listdir(filepath):
            remove_tree(os.path.join(filepath, subfile))
        os.rmdir(filepath)


def sync_tree(connection, repo_name, source, destination, rel_path, excludes, cache, config):
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
            logger.debug('%s: Skipping ignored file: %s' % (repo_name, relative_remote_path))
            continue
        elif shared_file.isDirectory:
            if not os.path.exists(full_local_path):
                logger.debug('Creating missing directory %s' % full_local_path)
                os.makedirs(full_local_path)

            if filename not in cache:
                cache[filename] = {}
            sync_tree(
                connection, repo_name, source, destination,
                os.path.join(rel_path, filename), excludes,
                cache[filename], config)
        else:
            remote_digest = "%s-%s" % (shared_file.file_size,
                                       shared_file.last_write_time)
            if os.path.exists(full_local_path) and filename in cache:
                if remote_digest == cache[filename]:
                    logger.debug(
                        '%s: File %s has not changed' % (repo_name, relative_remote_path))
                    continue
                if file_differs(full_local_path, cache[filename]):
                    handling_result = handle_local_change(
                        full_local_path, relative_remote_path,
                        config['conflict-handling'])
                    if (handling_result == 'keep'):
                        cache[filename] = remote_digest
                        continue
                    elif (handling_result == 'skip'):
                        continue

            cache[filename] = remote_digest
            full_remote_path = os.path.join(remote_path, filename)
            download_file(connection, full_remote_path, full_local_path)

            # set last write time to that of the remote file
            os.utime(
                full_local_path,
                (shared_file.last_access_time, shared_file.last_write_time))

    if fileset:  # if fileset not empty, remote files / folders have been deleted
        for filename in fileset:
            # TODO: handle recursively in case a whole directory is deleted
            del cache[filename]
            rel_path = os.path.join(rel_path, filename)
            full_path = os.path.join(destination, rel_path)
            logger.debug('%s: %s has been deleted on remote' % (repo_name, rel_path))
            if os.path.exists(full_path):
                conflict_handling = config['conflict-handling']['remote-deleted']
                if conflict_handling == 'ask':
                    question = ("%s has been deleted on remote. "
                                "Do you want to delete your local copy?")
                    answer = ask_question(question % os.path.join(repo_name, rel_path))
                    if answer is False:
                        return
                elif conflict_handling != 'delete':
                    return

                logger.info('%s: %s will be removed' % (repo_name, rel_path))
                remove_tree(full_path)


def sync(config):
    connection = smb_login(config)
    repositories = config['sync']['repositories']
    if not repositories:
        logger.info("No repositories in config")
    for name, repository in repositories.items():
        source = repository['remote-dir']
        destination = repository['local-dir']
        if not os.path.exists(destination):
            os.makedirs(destination)
        logger.info('Starting sync: %s -> %s' % (source, destination))
        excludes = config['sync']['global-exclude'] + repository['exclude']
        logger.info('The following patterns will be excluded: %s' % (excludes))
        cache_file = '%s/.%s.json' % (destination, name)
        cache = load_cache(cache_file)
        sync_tree(connection, name, source, destination, '', excludes, cache, config['sync'])
        dump_cache(cache_file, cache)
        logger.info("Sync of %s completed" % name)

    connection.close()


if __name__ == "__main__":
    config = configuration.load_config()
    sync(config)
