#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
import sys
import os
import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
from .exceptions import PrintException

# TODO: Load from CFG
sender = 'raphael.zimmermann@hsr.ch'

# These values are hard-coded to be updated easily in case of a change in the HSR infrastructure.
reciever = 'mobileprint@hsr.ch'
smtp_server = 'smtp.hsr.ch'


def create_pdf(full_path):
    """
        Creates a PDF from the given stdin into a file at full_path.
        If the conversion fails, an error is logged to stderr and the program quits with
        exit code 1.
    """

    command = ('gs -q -dNOPAUSE -dBATCH -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 '
               '-sPAPERSIZE=a4 -dPDFSETTINGS=/printer -sOutputFile=%s -c save pop -f'
               ' - &> /dev/null' % full_path)

    fpipe = os.popen(command)
    ret_code = fpipe.close()

    if ret_code is not None:
        print('ERROR: Failed to convert - return code was %s ' % ret_code, file=sys.stderr)
        sys.exit(1)


def send_email(full_path):
    """
    Sends the created pdf file as an email attachment. If an error has
    occured in the PDF creation process, it just sends a failure notice.
    """

    # Create the container (outer) email message.
    outer = MIMEMultipart()
    outer['Subject'] = 'PDF Print Request'
    outer['From'] = sender
    outer['To'] = reciever
    outer.preamble = 'PDF print request'

    msg = MIMEText('Print the attachment, please!\n\r', 'plain', 'utf-8')
    outer.attach(msg)

    # PDF ATTACHMENT PART
    fp = open(full_path, 'rb')
    msg = MIMEBase('application', 'pdf')
    msg.set_payload(fp.read())
    fp.close()
    encoders.encode_base64(msg)
    msg.add_header('Content-Disposition', 'attachment', filename=os.path.basename(full_path))
    outer.attach(msg)

    # Send the email via an SMTP server.
    s = smtplib.SMTP(smtp_server)
    s.starttls()
    # TODO: Authenticate in the future
    s.sendmail(sender, reciever, outer.as_string())
    s.quit()


def process():
    """
        This method shall be called by the cups backend backend.
    """

    # Print "device discovery" if called with no arguments
    if len(sys.argv) == 1:
        print('direct hsr-email-print "Unknown" "Print at HSR"')
        sys.exit(0)

    # Script must be alled with exactly 5 or 6 arguments
    if len(sys.argv) not in (5, 6):
        print('ERROR:Wrong number of arguments %s!' % sys.argv, file=sys.stderr)
        sys.exit(1)

    directory = os.environ['DEVICE_URI'].split(':')[1].strip()
    if not os.access(directory, os.W_OK):
        print('ERROR: No permission to write in %s!' % directory, file=sys.stderr)
        sys.exit(1)

    file_name = 'hsr-email-print-%s-%s.pdf' % (sys.argv[1], sys.argv[2])
    full_path = os.path.join(directory, file_name)

    # TODO: Input COULD also come via argv[6]?
    create_pdf(full_path)
    send_email(full_path)
