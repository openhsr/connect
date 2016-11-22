"""openhsr-connect
Usage:
  openhsr-connect sync [--local-changes=(ask|overwrite|keep|makeCopy)]
      [--remote-deleted=(ask|delete|keep)] [-q | -v]
  X openhsr-connect update-password
  openhsr-connect daemon [-d | --daemonize] [-q | -v]
  X openhsr-connect help
  X openhsr-connect edit
  X openhsr-connect -h | --help
  X openhsr-connect --version

Options:
X  -h --help             show this screen.
X  --version             show version.
X  -v --verbose          increase verbosity
X  -q --quiet            suppress non-error messages
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
import click
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


@click.group()
@click.version_option(version=__VERSION__)
@click.option('-v', '--verbose', is_flag=True, default=False, help='increase verbosity')
@click.option('-q', '--quiet', is_flag=True, default=False, help='suppress non-error messages')
@click.pass_context
def cli(ctx, verbose, quiet):
    setup_logging(verbose, quiet)
    logger.warning('WARNUNG: NOCH IST DIESE SOFTWARE IN ENTWICKLUNG - ALSO NICHT FÜR '
                   'DEN PRODUKTIVEN EINSATZ GEEIGNET!')

    ctx.obj['config'] = configuration.load_config()


@click.command(name='update-password')
@click.pass_context
def update_password(ctx):
    configuration.set_password(ctx.obj['config'])


@click.command()
@click.option('--daemonize', is_flag=True, default=False)
@click.pass_context
def daemon(ctx, daemonize):
    if daemonize:
        try:
            pid = os.fork()
            if pid > 0:
                logger.info('Forked to background!')
                sys.exit(0)
        except OSError as e:
            sys.stderr.write("fork #1 failed: %d (%s)\n" % (e.errno, e.strerror), file=sys.stderr)
            sys.exit(1)

    user_daemon.create_socket()


@click.command('sync')
@click.option('--local-changes', type=click.Choice(['ask', 'overwrite', 'keep', 'makeCopy']))
@click.option('--remote-deleted', type=click.Choice(['ask', 'delete', 'keep']))
@click.pass_context
def sync_command(ctx, local_changes, remote_deleted):
    if local_changes:
        ctx.obj['config']['sync']['conflict_handling']['local-changes'] = local_changes
    if remote_deleted:
        ctx.obj['config']['sync']['conflict_handling']['remote-deleted'] = remote_deleted
    sync.sync(ctx.obj['config'])


@click.command(name='help')
@click.pass_context
def browserhelp(ctx):
    webbrowser.open('https://github.com/openhsr/connect/tree/master/docs')


@click.command()
@click.pass_context
def edit(ctx):
    configuration.edit(ctx.obj['config'])


def setup_logging(verbose, quiet):
    logger.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    formatter = logging.Formatter('%(message)s')
    if verbose and not quiet:
        logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('[%(levelname)-7s] %(message)s')
    if quiet:
        logger.setLevel(logging.WARNING)

    ch.setFormatter(formatter)
    logger.addHandler(ch)
    logger.debug("Setting up logging complete")


def main():
    try:
        cli.add_command(sync_command)
        cli.add_command(update_password)
        cli.add_command(daemon)
        cli.add_command(edit)
        cli.add_command(browserhelp)
        cli(obj={}, standalone_mode=False)
    except Exception as e:
        logger.error(e)
        logger.debug(e, exc_info=True)
        exit(1)

if __name__ == '__main__':
    main()
