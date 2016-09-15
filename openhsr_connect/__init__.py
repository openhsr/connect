"""openHSR-connect
Usage:
  openhsr-connect sync [--local-changes=(ask|overwrite|keep|makeCopy)]
      [--remote-deleted=(ask|delete|keep)] [repository]
  openhsr-connect print (install|remove) [<printer_name>]
  openhsr-connect daemon [-d | --daemonize]
  openhsr-connect help (sync|vpn|print)
  openhsr-connect -h | --help
  openhsr-connect --version

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

__VERSION__ = '0.0.1.dev'

from docopt import docopt
import yaml


def merge(dict_1, dict_2):
    return dict((str(key), dict_1.get(key) or dict_2.get(key))
                for key in set(dict_2) | set(dict_1))


def main():
    arguments = docopt(__doc__, version='openHSR-connect %s' % __VERSION__)
    config = yaml.load(open('openhsr_connect/etc/config.yml'))
    result = merge(arguments, config)

    print("test")
    print(arguments)
    print(config)
    print(result)

main()
