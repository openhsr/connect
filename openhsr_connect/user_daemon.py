import os
import socket
import json
import logging
import struct

from openhsr_connect import printing
from openhsr_connect.exceptions import PrintException
from openhsr_connect import configuration

logger = logging.getLogger('openhsr_connect.print')


def create_socket():
    """
    Create a socket and listen to any connection.
    The socket accepts connections from the CUPS Backend, sending JSON-Objects
    over the connection.
    This allows us to handle the printing in the user space - access passwords safely and
    display (if required) warnings to the user.
    """
    socketpath = '/var/run/user/%s/openhsr-connect.sock' % str(os.getuid())
    try:
        os.remove(socketpath)
    except OSError:
        pass

    filesocket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

    filesocket.bind(socketpath)
    filesocket.listen(0)  # TODO or 1? maximum queued connections

    while True:
        conn, addr = filesocket.accept()
        meta, payload = read_data(conn)
        try:
            config = configuration.load_config(raise_if_incomplete=True)
            password = configuration.get_password(config)
            printing.send_to_printer(config, password, meta, payload)
        except PrintException as e:
            logger.error('Exception occured during send_to_printer: \n%s ' % e)


def read_data(conn):
    """
    Reads the data from the socket. The CUPS-Backend sends a utf-8 binary encoded string
    with a json object containing the .ps file to print as well as other meta information for
    the print.
    This method reads all the data and returns the parsed JSON object.
    """
    header_length_b = conn.recv(8)
    header_length = struct.unpack('<q', header_length_b)[0]
    logger.debug("received header length: {0}(Binary {1})".format(header_length, header_length_b))

    raw = conn.recv(header_length)
    header = json.loads(raw.decode())
    logger.debug("received header: {0}".format(header))

    binary = b''
    while True:
        bufsize = 1024
        temp = conn.recv(bufsize)
        binary += temp
        logger.debug("recieved {} bytes...".format(len(temp)))
        if (len(temp) < bufsize):
            break
    return (header, binary)
