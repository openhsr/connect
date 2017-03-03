import os
import socket
from smb.SMBConnection import SMBConnection
from smb.smb_structs import ProtocolError

from openhsr_connect import sync
from openhsr_connect import configuration
from openhsr_connect import exceptions


class SMB_Sync(sync.Sync):

    SMB_SERVER_NAME = 'c206.hsr.ch'
    SMB_SHARE_NAME = 'skripte'
    SMB_DOMAIN = 'HSR'
    SMB_SERVER_PORT = 445

    def connect(self):
        username = self.config['login']['username']
        password = configuration.get_password(self.config)
        try:
            server_ip = socket.gethostbyname(self.SMB_SERVER_NAME)
        except OSError as e:
            self.logger.debug("Exception when connecting to %s: %s" % (self.SMB_SERVER_NAME, e))
            raise exceptions.ConnectException(
                'Could not find %s, are you in the HSR network?' % self.SMB_SERVER_NAME)

        client_name = socket.gethostname()
        connection = SMBConnection(
            username, password, client_name,
            self.SMB_SERVER_NAME, domain=self.SMB_DOMAIN, use_ntlm_v2=False, is_direct_tcp=True)
        try:
            connect_result = connection.connect(server_ip, self.SMB_SERVER_PORT)
            if connect_result is False:
                raise ProtocolError("SMB Connection failure")
        except ProtocolError as e:
            self.logger.debug("Exception when connecting to %s: %s" % (self.SMB_SERVER_NAME, e))
            raise exceptions.ConnectException(
                "Connection to %s failed, wrong password?" % self.SMB_SERVER_NAME)
        self.logger.debug('SMB Connection to %s successful!' % self.SMB_SERVER_NAME)
        return connection

    def dispose(self):
        self.connection.close()

    def create_local_digest(self, path):
        # parse mtime to int (seconds) to avoid precision errors
        mtime = int(os.path.getmtime(path))
        return "%s-%s" % (os.path.getsize(path), mtime)

    def create_remote_digest(self, path):
        attributes = self.connection.getAttributes(self.SMB_SHARE_NAME, path)
        # parse last_write_time to int (seconds) to avoid precision errors
        mtime = int(attributes.last_write_time)
        return "%s-%s" % (attributes.file_size, mtime)

    def list_path(self, path):
        path_listing = self.connection.listPath(self.SMB_SHARE_NAME, path)
        files_folders = filter(lambda f: f.filename != '.' and f.filename != '..', path_listing)

        def file_entry(f): return {'filename': f.filename, 'last_write_time': f.last_write_time}
        directories = []
        files = []
        [directories.append(f.filename) if f.isDirectory else files.append(file_entry(f))
            for f in files_folders]
        return directories, files

    def retrieve_file(self, remote_path, local_path):
        with open(local_path, 'wb') as local_file:
            self.connection.retrieveFile(self.SMB_SHARE_NAME, remote_path, local_file)
            self.logger.debug('Downloading of file %s complete!' % remote_path)
