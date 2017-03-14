import os
from subprocess import Popen, PIPE
import logging

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders

from openhsr_connect.exceptions import PrintException

# These values are hard-coded to be updated easily in case of a change in the HSR infrastructure.
reciever = 'mobileprint@hsr.ch'
smtp_server = 'smtp.hsr.ch'

logger = logging.getLogger('openhsr_connect.print')


def send_to_printer(config, password, meta, payload):
    """
    This method shall be called by the cups backend backend.
    As input, the "data" object sent from the cups backend is expected

    This method can throw a PrintException that must be caughted by the daemon.
    """

    file_name = 'openhsr-connect-%s-%s.pdf' % (meta['id'], meta['user'])
    full_path = os.path.join(meta['directory'], file_name)

    create_pdf(full_path, payload)
    send_email(full_path, config['login']['email'], config['login']['username'], password)

    # Remove PDF file when sent
    os.remove(full_path)


def create_pdf(full_path, raw):
    """
    Creates a PDF from the given stdin into a file at full_path.
    If the conversion fails, an error is logged to stderr and the program quits with
    exit code 1.
    """

    command = ['gs', '-q', '-dNOPAUSE', '-dBATCH', '-sDEVICE=pdfwrite', '-dCompatibilityLevel=1.4',
               '-sPAPERSIZE=a4', '-dPDFSETTINGS=/printer', '-sOutputFile=%s' % full_path,
               '-c', 'save', 'pop', '-f', '-']

    # Pipe the raw postscript data into gs
    p = Popen(command, stdout=PIPE, stdin=PIPE, stderr=PIPE)
    stdout_data = p.communicate(input=raw)[0].decode('utf-8')

    # Verify exit code and output
    if p.returncode != 0 or len(stdout_data) > 0:
        logger.error('Failed to convert - return code was %s, output: \n%s ' %
                     (p.returncode, stdout_data))
        raise PrintException('PDF conversion failed')


def send_email(full_path, sender, user,  password):
    """
    Sends the created pdf file as an email attachment. If an error has
    occured in the PDF creation process, it just sends a failure notice.
    """

    try:
        # Create the container (outer) email message.
        outer = MIMEMultipart()
        outer['Subject'] = 'PDF Print Request'
        outer['From'] = sender
        outer['To'] = reciever
        outer.preamble = 'PDF print request'

        msg = MIMEText('Print the attachment, please!\n\r', 'plain', 'utf-8')
        outer.attach(msg)

        # PDF attachment part
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
        s.login(user, password)
        s.sendmail(sender, reciever, outer.as_string())
        logger.info('E-Mail to %s sent!' % reciever)
        s.quit()
    except Exception as e:
        raise PrintException(e)
