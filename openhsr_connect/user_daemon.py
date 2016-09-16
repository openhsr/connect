#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import socket
import json
import logging
from . import printing
from .exceptions import PrintException


logger = logging.getLogger('openhsr_connect.print')

# TODO: When should we close the socket
# conn.close()


def create_socket():

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
        data = read_data(conn)

        try:
            printing.send_to_printer(data)
        except PrintException as e:
            logger.error('Exception occured during send_to_printer: \n%s ' % e)


def read_data(conn):
    binary = b''
    while True:
        bufsize = 1024
        temp = conn.recv(bufsize)
        print(temp)
        binary += temp
        if (len(temp) < bufsize):
            break

    return json.loads(binary.decode('utf-8'))

if __name__ == '__main__':
    create_socket()
