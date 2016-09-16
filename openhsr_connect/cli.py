"""openHSR-connect
Usage:
  openhsr-connect sync [--local-changes=(ask|overwrite|keep|makeCopy)]
      [--remote-deleted=(ask|delete|keep)] [repository]
  openhsr-connect print (install|remove) [<printer_name>]
  openhsr-connect daemon [-d | --daemonize]
  openhsr-connect help (sync|vpn|print)
  openhsr-connect -h | --help
  openhsr-connect --version
  openhsr-connect update-password

Options:
  -h --help             show this screen.
  --version             show version.
  -v --verbose          increase verbosity
  -q --quiet            suppress non-error messages
  --local-changes=<a>   sync behaviour on local file modifications
                        and new remote file [default: <ask>]
                        options for <a> are: ask, overwrite, keep, makeCopy
                        where "keep" keeps only your local File
                        and "makeCopy" keeps both local and remote Files
  --remote-deleted=<a>  sync behaviour on remote file removes.
                        Options for <a> are: ask, delete, keep
  -d --daemonize        runs daemon in background

"""
from docopt import docopt
import traceback
import jsonschema
from . import config
from . import __VERSION__


def main():
    try:
        arguments = docopt(__doc__, version='openhsr-connect %s' % __VERSION__)
        config.load_config()

        # TODO: override configuration!

    except jsonschema.exceptions.ValidationError as e:
        print('Your configuration file is invalid:')
        print(e.message)
    except Exception as e:
        traceback.print_exc()
        print('\n\nopenhsr-connect has crashed :(')
        print('Please report at https://github.com/openhsr/connect/issues/')

if __name__ == '__main__':
    main()
