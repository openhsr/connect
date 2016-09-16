import yaml
import os
import logging
import getpass
import keyring
from .exceptions import PasswordException
import jsonschema

logger = logging.getLogger('openhsr_connect.config')


DEFAULT_CONFIG = """
login:
  username: {username}
  email: {mail}

sync:
  global_exclude:
    - .DS_Store
    - Thumbs.db

  conflict_handling:
    local-changes: ask # ask | keep | overwrite | makeCopy
    remote-deleted: ask # ask | delete | keep
"""

SCHEMA = {
    'title': 'open\HSR Connect configuration Schema',
    'type': 'object',
    'properties': {
        'login': {
            'type': 'object',
            'properties': {
                'username': {
                    'type': 'string'
                },
                'email': {
                    'type': 'string',
                    'pattern': '^[a-zA-Z0-9]+\.[a-zA-Z0-9]+\@hsr.ch$'
                }
            },
            'required': ['username', 'email']
        },
        'sync': {
            'type': 'object',
            'properties': {
                'global_exclude': {
                    'type': 'array',
                    'items': {'type': 'string'},
                },
                'conflict_handling': {
                    'type': 'object',
                    'properties': {
                        'local-changes': {
                            'type': 'string',
                            'pattern': '^(ask|keep|overwrite|makeCopy)$'
                        },
                        'remote-deleted': {
                            'type': 'string',
                            'pattern': '^(ask|delete|keep)$'
                        }
                    },
                    'additionalProperties': False
                },
                'repositories': {
                    'type': 'object',
                    'patternProperties': {
                        '^[^\/*&%\s]+$': {
                            'type': 'object',
                            'properties': {
                                'remote_dir': {'type': 'string'},
                                'local_dir': {'type': 'string'},
                                'exclude': {
                                    'type': 'array',
                                    'items': {'type': 'string'},
                                }
                            },
                            'required': ['remote_dir', 'local_dir']
                        }
                    },
                    'additionalProperties': False
                }
            },
            'additionalProperties': False
        }
    },
    'additionalProperties': False,
    'required': ['login', 'sync']
}


def create_default_config(config_path):
    """
    Creates the a default configuration file.
    Prompts for input (username and mail)
    """
    logger.info('Creating default configuration')
    username = input('Dein HSR-Benutzername: ')
    mail = input('Deine HSR-Email (VORNAME.NACHNAME@hsr.ch): ')
    config = DEFAULT_CONFIG.format(username=username, mail=mail)
    with open(config_path, 'w') as f:
        f.write(config)


def load_config(raise_if_incomplete=False):
    """
    Loads the user configuration and creates the default configuration if it does not yet exist.
    """
    config_path = os.path.expanduser('~/.config/openhsr-connect.yaml')

    # create default config if it does not yet exist
    if not os.path.exists(config_path):
        create_default_config(config_path)

    configuration = None
    with open(config_path, 'r') as f:
        if raise_if_incomplete:
            raise ConfigurationException('Configuration does not yet exist!')
        configuration = yaml.load(f)

    # Verify if the password is in the keyring
    try:
        get_password(configuration)
    except PasswordException as e:
        if raise_if_incomplete:
            raise e
        password = getpass.getpass('Dein HSR-Kennwort (wird sicher im Keyring gespeichert): ')
        keyring.set_password('openhsr-connect', configuration['login']['username'], password)

    # Validate the configuration
    jsonschema.validate(configuration, SCHEMA)

    # if "global_exclude" is not (fully) declared:
    if 'global_exclude' not in configuration['sync']:
        configuration['sync']['global_exclude'] = []

    # if "conflict_handling" is not (fully) declared:
    if 'conflict_handling' not in configuration['sync']:
        configuration['sync']['conflict_handling'] = {}
    if 'local-changes' not in configuration['sync']['conflict_handling']:
        configuration['sync']['conflict_handling']['local-changes'] = 'keep'
    if 'remote-deleted' not in configuration['sync']['conflict_handling']:
        configuration['sync']['conflict_handling']['remote-deleted'] = 'delete'

    # if repositories is not (fully) declared
    if 'repositories' not in configuration['sync']:
        configuration['sync']['repositories'] = {}

    for name, repository in configuration['sync']['repositories'].items():
        if 'exclude' not in repository:
            repository['exclude'] = []
    return configuration


def get_password(configuration):
    """
        This method can throw a PasswordException
    """
    password = keyring.get_password('openhsr-connect', configuration['login']['username'])
    if password is None:
        raise PasswordException('No password found for user %s' %
                                configuration['login']['username'])
    else:
        return password
