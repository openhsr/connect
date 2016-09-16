"""openhsr-connect
Usage:
  openhsr-connect sync [--local-changes=(ask|overwrite|keep|makeCopy)]
      [--remote-deleted=(ask|delete|keep)] [repository]
  openhsr-connect daemon [-d | --daemonize]
  openhsr-connect help
  openhsr-connect -h | --help
  openhsr-connect --version
  openhsr-connect update-password

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
import jsonschema
import webbrowser
import sys
from . import configuration
from . import sync
from . import __VERSION__


def main():
    try:
        arguments = docopt(__doc__, version='openhsr-connect %s' % __VERSION__)
        config = configuration.load_config()

        # print(arguments)
        if arguments['help']:
            webbrowser.open('https://github.com/openhsr/connect/tree/master/docs')
        if arguments['sync']:
            if arguments['--local-changes']:
                if arguments['--local-changes'] not in ['ask', 'delete', 'keep']:
                    print('%s is not a valid value for local-changes'
                          % arguments['--local-changes'], file=sys.stderr)
                    sys.exit(1)
                config['sync']['conflict_handling']['local-changes'] = arguments['--local-changes']
            if arguments['--remote-deleted']:
                if arguments['--remote-deleted'] not in ['ask', 'keep', 'overwrite', 'makeCopy']:
                    print('%s is not a valid value for remote-deleted'
                          % arguments['--remote-deleted'], file=sys.stderr)
                    sys.exit(1)
                config['sync']['conflict_handling']['remote-deleted'] = arguments['--remote-deleted']
            sync.sync(config)
    except jsonschema.exceptions.ValidationError as e:
        print('Your configuration file is invalid:', file=sys.stderr)
        print(e.message, file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        traceback.print_exc()
        print('\n\nopenhsr-connect has crashed :(', file=sys.stderr)
        print('Please report at https://github.com/openhsr/connect/issues/', file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
