import os
import os.path
from datetime import datetime
import logging
import json
import fnmatch
import shutil


class Sync:
    """ Abstract Sync class, uses Template Method Pattern """

    def __init__(self, config):
        self.logger = logging.getLogger('openhsr_connect.sync')
        self.config = config
        self.connection = self.connect()

    def connect(self):
        """ return connection """
        raise NotImplementedError()

    def dispose(self):
        """ dispose connection"""
        pass

    def create_local_digest(self, path):
        raise NotImplementedError()

    def create_remote_digest(self, path):
        raise NotImplementedError()

    def retrieve_file(self, remote_path, local_path):
        raise NotImplementedError()

    def list_path(self, path):
        """ Return a tuple with subdirectories and a list of files

        A file is a dict with attributes filename, last_write_time
        """
        raise NotImplementedError()

    def load_cache(self, filename):
        cache = {}
        if os.path.exists(filename):
            with open(filename, 'r') as fp:
                cache = json.load(fp)
        return cache

    def dump_cache(self, filename, cache):
        with open(filename, 'w') as fp:
            json.dump(cache, fp)

    def cache_entry(self, digest, ignore=False):
        return {'hash': digest, 'ignore': ignore}

    def exclude_path(self, path, excludes):
        filename = os.path.split(path)[1]
        for exclude in excludes:
            if exclude.startswith('/'):
                if path.startswith(exclude[1:]):
                    return True
            elif '/' in exclude:
                if exclude in path:
                    return True
            elif fnmatch.fnmatch(filename, exclude):
                return True
        return False

    def ask_question(self, question):
        while True:
            choice = input("%s (y/N)" % question)
            choice = choice.lower()
            if choice == '' or choice == 'n':
                return False
            elif choice == 'y':
                return True

    def get_copy_filename(self, path):
        date = datetime.now().strftime("%y%m%d%H%M")
        filename, extension = os.path.splitext(path)
        return "%s-local-%s%s" % (filename, date, extension)

    def file_has_local_changes(self, local_path, current_digest):
        return current_digest != self.create_local_digest(local_path)

    def handle_local_change(self, full_local_path, rel_remote_path):
        self.logger.debug('File %s has changed locally or it has been added to the index' % rel_remote_path)
        handling_config = self.config['sync']['conflict-handling']['local-changes']
        if handling_config == 'keep':
            return 'keep'
        elif handling_config == 'ask':
            question = "Do you want to overwrite %s with the version from the server?"
            if not self.ask_question(question % full_local_path):
                return 'keep'
            self.logger.debug("File %s will be overwritten" % full_local_path)
            return 'overwrite'
        elif handling_config == 'overwrite':
            self.logger.info("File %s will be overwritten" % full_local_path)
            return 'overwrite'
        elif handling_config == 'makeCopy':
            new_filename = self.get_copy_filename(full_local_path)
            self.logger.debug("Rename local file %s to %s" % (full_local_path, new_filename))
            os.rename(full_local_path, new_filename)
            return 'makeCopy'
        return 'keep'  # just in case a wrong config is given

    def handle_deleted_files(self, fileset, repo_name, rel_path, destination, cache):
        for filename in fileset:
            if 'ignore' in cache[filename] and cache[filename]['ignore']:
                continue
            relative_path = os.path.join(rel_path, filename)
            full_path = os.path.join(destination, relative_path)
            self.logger.debug('%s: %s has been deleted on remote' % (repo_name, relative_path))
            if os.path.exists(full_path):
                conflict_handling = self.config['sync']['conflict-handling']['remote-deleted']
                if conflict_handling == 'ask':
                    question = ("%s has been deleted on remote. "
                                "Do you want to delete your local copy?")
                    answer = self.ask_question(question % os.path.join(repo_name, relative_path))
                    if answer is False:
                        cache[filename]['ignore'] = True
                        continue
                elif conflict_handling != 'delete':
                    cache[filename]['ignore'] = True
                    continue

                self.logger.info('%s: %s will be removed' % (repo_name, relative_path))
                os.remove(full_path) if os.path.isfile(full_path) else shutil.rmtree(full_path)
                del cache[filename]

    def sync_tree(self, repo_name, source, destination, rel_path, excludes, cache):
        fileset = set(cache)
        remote_path = os.path.join(source, rel_path)
        remote_directories, remote_files = self.list_path(remote_path)
        for remote_dir in remote_directories:
            fileset.discard(remote_dir)
            relative_remote_path = os.path.join(rel_path, remote_dir)
            if self.exclude_path(relative_remote_path, excludes):
                self.logger.debug('%s: Skipping ignored folder: %s' % (repo_name, relative_remote_path))
                continue
            full_local_path = os.path.join(destination, rel_path, remote_dir)
            if not os.path.exists(full_local_path):
                self.logger.debug('Creating missing directory %s' % full_local_path)
                os.makedirs(full_local_path)
            if remote_dir not in cache:
                cache[remote_dir] = {}
            # recursive call to sync the subfolder
            self.sync_tree(
                repo_name, source, destination,
                os.path.join(rel_path, remote_dir), excludes,
                cache[remote_dir])

        for remote_file in remote_files:
            filename = remote_file['filename']
            fileset.discard(filename)
            relative_remote_path = os.path.join(rel_path, filename)
            full_remote_path = os.path.join(remote_path, filename)
            full_local_path = os.path.join(destination, rel_path, filename)
            if self.exclude_path(relative_remote_path, excludes):
                self.logger.debug('%s: Skipping ignored file: %s' % (repo_name, relative_remote_path))
                continue
            remote_digest = self.create_remote_digest(full_remote_path)
            if os.path.exists(full_local_path):
                is_existing_file = False
                if filename not in cache:
                    # already existing local file
                    self.logger.info('%s: Add existing file to index: %s' %
                                     (repo_name, relative_remote_path))
                    cache[filename] = self.cache_entry(self.create_local_digest(full_local_path))
                    is_existing_file = True
                if cache[filename]['ignore']:
                    continue
                if remote_digest == cache[filename]['hash']:
                    self.logger.debug(
                        '%s: File %s has not changed' % (repo_name, relative_remote_path))
                    continue
                if self.file_has_local_changes(full_local_path, cache[filename]['hash']) \
                        or is_existing_file:
                    handling_result = self.handle_local_change(
                        full_local_path, relative_remote_path)
                    if handling_result == 'keep':
                        cache[filename]['ignore'] = True
                        continue

            cache[filename] = self.cache_entry(remote_digest)

            self.logger.info('Downloading file %s' % full_remote_path)
            self.retrieve_file(full_remote_path, full_local_path)

            # set last write time to that of the remote file
            os.utime(
                full_local_path,
                (remote_file['last_write_time'], remote_file['last_write_time']))

        if fileset:  # if fileset not empty, remote files / folders have been deleted
            self.handle_deleted_files(fileset, repo_name, rel_path, destination, cache)

    def sync(self):
        repositories = self.config['sync']['repositories']
        if not repositories:
            self.logger.info("No repositories in config")
        for name, repository in sorted(repositories.items()):
            source = repository['remote-dir']
            destination = os.path.expanduser(repository['local-dir'])
            if not os.path.exists(destination):
                os.makedirs(destination)
            self.logger.info('Starting sync: %s -> %s' % (source, destination))
            excludes = self.config['sync']['global-exclude'] + repository['exclude']
            self.logger.info('The following patterns will be excluded: %s' % (excludes))
            cache_file = '%s/.%s.json' % (destination, name)
            cache = self.load_cache(cache_file)
            self.sync_tree(name, source, destination, '', excludes, cache)
            self.dump_cache(cache_file, cache)
            self.logger.info("Sync of %s completed" % name)

        self.dispose()