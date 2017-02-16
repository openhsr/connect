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
from . import smb_sync
from . import __VERSION__

logger = logging.getLogger('openhsr_connect')


@click.group(context_settings={'help_option_names': ['-h', '--help']})
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
    smb_syncer = smb_sync.SMB_Sync(ctx.obj['config'])
    smb_syncer.sync()


@click.command(name='help', help="Open the Documentation in the Browser")
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
