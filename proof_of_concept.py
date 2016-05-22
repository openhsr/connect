import os
import socket
import logging
import hashlib
import json

from smb.SMBConnection import SMBConnection

# create Logger
logger = logging.getLogger('connect')
logger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
formatter = logging.Formatter('[%(levelname)s] [%(name)s]  %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# SMB Data
SMB_USER_ID = ''
SMB_USER_PASSWORD = ''
SMB_SERVER_IP = '152.96.90.26'
SMB_SERVER_NAME = ''
SMB_SHARE_NAME = 'skripte'
SMB_CLIENT_NAME = socket.gethostname()
SMB_DOMAIN = 'HSR'
SMB_SERVER_PORT = 445


def sync_tree(connection, source, destination, excludes, cache):
    # TODO: What if a file is remotely deleted? Is this even relevant?
    for shared_file in connection.listPath(SMB_SHARE_NAME, source):
        full_remote_path = source + '/' + shared_file.filename
        full_local_path = destination + '/' + shared_file.filename
        if shared_file.filename == '.' or shared_file.filename == '..':
            continue
        elif shared_file.filename in excludes:
            # TODO: Support for wildcards!
            logger.debug('Skipping ignored file: %s' % full_remote_path)
            continue
        elif shared_file.isDirectory:
            if not os.path.exists(full_local_path):
                logger.debug('Creating missing directory %s' % full_local_path)
                os.makedirs(full_local_path)
            sync_tree(connection, full_remote_path, full_local_path, excludes)
        else:
            m = hashlib.md5()
            m.update(str(shared_file.file_size).encode('utf-8'))
            m.update(str(shared_file.last_write_time).encode('utf-8'))
            m.update(str(shared_file.last_write_time).encode('utf-8'))
            new_digest = m.hexdigest()

            if full_remote_path in cache and new_digest == cache[full_remote_path]:
                logger.debug('File %s has not changed' % full_remote_path)
                continue

            logger.debug('Downloading file %s' % full_remote_path)
            with open(full_local_path, 'wb') as local_file:
                connection.retrieveFile(SMB_SHARE_NAME, full_remote_path, local_file)
                cache[full_remote_path] = new_digest
                logger.debug('Downloading of file %s complete!' % full_remote_path)


global_exclude = ['.DS_Store', 'Thumbs.db']

# source (leading and tiling slash are optional - both methods work!)
source = 'Informatik/Fachbereich/Informationssicherheit_1_-_Grundlagen/InfSi1/Admin/'
# Local destination shall not have a tiling slash!
destination = 'synced/InfSi1/Admin'
local_exclude = ['*.exe', 'Archiv']

if not os.path.exists(destination):
    logger.info("Creating directory %s" % destination)
    os.makedirs(destination)

cache = {}
if os.path.exists(destination + '.json'):
    with open(destination + '.json', 'r') as fp:
        cache = json.load(fp)

logger.info('Establishing connection...')
connection = SMBConnection(SMB_USER_ID, SMB_USER_PASSWORD, SMB_CLIENT_NAME, SMB_SERVER_NAME,
                           domain=SMB_DOMAIN, use_ntlm_v2=False)
assert connection.connect(SMB_SERVER_IP, SMB_SERVER_PORT)
logger.info('Connection successful!')

# Let's sync!
logger.info('Starting sync: %s -> %s' % (source, destination))
excludes = global_exclude + local_exclude
logger.info('The following patterns will be excluded: %s' % (excludes))
sync_tree(connection, source, destination, excludes, cache)

with open(destination + '.json', 'w') as fp:
    json.dump(cache, fp)

connection.close()
