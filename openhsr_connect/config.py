import yaml
import os
import logging
import getpass
import keyring
from .exceptions import PasswordException


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
    local-changes: keep # ask | keep | overwrite | makeCopy
    remote-deleted: delete # delete | keep
"""


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


def load_config():
    """
    Loads the user configuration and creates the default configuration if it does not yet exist.
    """
    config_path = os.path.expanduser('~/.config/openhsr-connect.yaml')

    # create default config if it does not yet exist
    if not os.path.exists(config_path):
        create_default_config(config_path)

    configuration = None
    with open(config_path, 'r') as f:
        configuration = yaml.load(f)

    # Verify if the password is in the keyring
    try:
        get_password(configuration)
    except PasswordException as e:
        password = getpass.getpass('Dein HSR-Kennwort (wird sicher im Keyring gespeichert): ')
        keyring.set_password('openhsr-connect', configuration['login']['username'], password)

    # TODO: validate the configuration (JSON SCHEMA)


def get_password(configuration):
    """
        This method can throw a PasswordException
    """
    password = keyring.get_password('openhsr-connect', configuration['login']['username'])
    if password is None:
        raise PasswordException('No password found for user %s' % username)
    else:
        return password
