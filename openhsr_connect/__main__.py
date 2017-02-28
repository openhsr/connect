import click
import os
import webbrowser
import sys
import logging
from openhsr_connect import configuration
from openhsr_connect import user_daemon
from openhsr_connect import smb_sync
from openhsr_connect import __VERSION__
from openhsr_connect import exceptions

logger = logging.getLogger('openhsr_connect')


@click.group(context_settings={'help_option_names': ['-h', '--help']})
@click.version_option(version=__VERSION__)
@click.option('-v', '--verbose', is_flag=True, default=False, help='increase verbosity')
@click.option('-q', '--quiet', is_flag=True, default=False, help='suppress non-error messages')
def cli(verbose, quiet):
    setup_logging(verbose, quiet)
    logger.warning('WARNUNG: NOCH IST DIESE SOFTWARE IN ENTWICKLUNG - ALSO NICHT FÜR '
                   'DEN PRODUKTIVEN EINSATZ GEEIGNET!')


@click.command(name='update-password')
def update_password():
    configuration.set_password(configuration.load_config())


@click.command()
@click.option('--daemonize', is_flag=True, default=False)
def daemon(daemonize):
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
def sync_command(local_changes, remote_deleted):
    config = configuration.load_config()
    if local_changes:
        config['sync']['conflict_handling']['local-changes'] = local_changes
    if remote_deleted:
        config['sync']['conflict_handling']['remote-deleted'] = remote_deleted
    smb_syncer = smb_sync.SMB_Sync(config)
    smb_syncer.sync()


@click.command(name='help', help="Open the Documentation in the Browser")
def browserhelp():
    webbrowser.open('https://openhsr-connect.readthedocs.io/de/latest/')


@click.command()
def edit():
    configuration.edit()


def setup_logging(verbose, quiet):
    logger.setLevel(logging.INFO)
    ch = logging.StreamHandler(sys.stdout)
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
        cli(standalone_mode=False)
    except click.UsageError as e:
        e.show()
        exit(1)
    except (exceptions.Error, click.ClickException) as e:
        logger.error(e)
        logger.debug(e, exc_info=True)
        exit(1)


if __name__ == '__main__':
    main()
