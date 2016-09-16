"""openhsr-connect
Usage:
  openhsr-connect sync [--local-changes=(ask|overwrite|keep|makeCopy)]
      [--remote-deleted=(ask|delete|keep)] [-q | -v]
  openhsr-connect update-password
  openhsr-connect daemon [-d | --daemonize] [-q | -v]
  openhsr-connect help
  openhsr-connect -h | --help
  openhsr-connect --version

Options:
  -h --help             show this screen.
  --version             show version.
  -v --verbose          increase verbosity
  -q --quiet            suppress non-error messages
  --local-changes=<a>   sync behaviour on local file modifications
                        and new remote file
                        options for <a> are: ask, overwrite, keep, makeCopy
                        where "keep" keeps only your local File
                        and "makeCopy" keeps both local and remote Files
                        The default value is loaded from the configuration file.
  --remote-deleted=<a>  sync behaviour on remote file removes.
                        Options for <a> are: ask, delete, keep.
                        The default value is loaded from the configuration file.
  -d --daemonize        runs daemon in background

The configuration file is located in `~/.config/openhsr-connect.yaml`

"""
from docopt import docopt
import traceback
import os
import jsonschema
import webbrowser
import sys
import logging
from .exceptions import ConnectException
from . import configuration
from . import user_daemon
from . import sync
from . import __VERSION__

logger = logging.getLogger('openhsr_connect')


def main():
    try:
        logger.setLevel(logging.INFO)
        arguments = docopt(__doc__, version='openhsr-connect %s' % __VERSION__)
        logger.warning('WARNUNG: NOCH IST DIESE SOFTWARE IN ENTWICKLUNG - ALSO NICHT FÜR'
                       'DEN PRODUKTIVEN EINSATZ GEEIGNET!')
        if arguments['--verbose']:
            logger.setLevel(logging.DEBUG)
        if arguments['--quiet']:
            logger.setLevel(logging.WARNING)

        config = configuration.load_config()
        logging.debug('debug stuff...')

        if arguments['help']:
            webbrowser.open('https://github.com/openhsr/connect/tree/master/docs')
        if arguments['update-password']:
            configuration.set_password(config)
        if arguments['sync']:
            if arguments['--local-changes']:
                if arguments['--local-changes'] not in ['ask', 'delete', 'keep']:
                    logger.error('%s is not a valid value for local-changes'
                                 % arguments['--local-changes'])
                    sys.exit(1)
                config['sync']['conflict_handling']['local-changes'] = arguments['--local-changes']
            if arguments['--remote-deleted']:
                if arguments['--remote-deleted'] not in ['ask', 'keep', 'overwrite', 'makeCopy']:
                    logger.error('%s is not a valid value for remote-deleted'
                                 % arguments['--remote-deleted'], file=sys.stderr)
                    sys.exit(1)
                config['sync']['conflict_handling']['remote-deleted'] = arguments['--remote-deleted']
            sync.sync(config)
        if arguments['daemon']:
            if arguments['--daemonize']:
                try:
                    pid = os.fork()
                    if pid > 0:
                        logger.info('Forked to background!')
                        sys.exit(0)
                except OSError as e:
                        sys.stderr.write("fork #1 failed: %d (%s)\n" % (e.errno, e.strerror), file=sys.stderr)
                        sys.exit(1)
            user_daemon.create_socket()
    except jsonschema.exceptions.ValidationError as e:
        logger.error('Your configuration file is invalid:')
        logger.error(e.message)
        sys.exit(1)
    except ConnectException as e:
        logger.error(e)
        sys.exit(1)
    except Exception as e:
        traceback.print_exc()
        logger.error('\n\nopenhsr-connect has crashed :(')
        logger.error('Please report at https://github.com/openhsr/connect/issues/')
        sys.exit(1)

if __name__ == '__main__':
    main()
