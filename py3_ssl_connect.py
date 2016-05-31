# Python 3 script to connect to a specified site and output whatever dict values are returned, and to
#     send an email notification.
# In this example the output is: valid from, valid until, full dict, and number of days until expiry.
# This can be the basis of a cron job to send an email notification if a cert expires within x days.
# A cron job would require some handling of the SMTP password?
# To-do:  better error checking, make it less gullible. try/except the SMTP connection.

import ssl
import socket
import argparse
import pprint
import smtplib
import getpass
from datetime import datetime

parser = argparse.ArgumentParser(description='Specify a site to connect to.')
parser.add_argument('host', help='Add the name of the site you want to connect to')
parser.add_argument('-p', '--port', help='Specify a port to connect to', type=int, default=443)
args=parser.parse_args()

email_login = 'example@example.com'
email_pass = getpass.getpass('Enter SMTP password for %s: ' % email_login)
smtp_server = 'smtp.example.com'
email_recipient = 'example_recipient@example.com'

def send_email(body):
    smtp_job = smtplib.SMTP(smtp_server, 587)
    smtp_job.ehlo()
    smtp_job.starttls()
    smtp_job.login(email_login, email_pass)
    smtp_job.sendmail(email_login, email_recipient, body)
    smtp_job.quit()

if args.host and args.port:
    print( '#' * 20 + '\n' + 'Trying to connect to:  %s:%s \n' % (args.host,args.port))
    
def exit_error(error_code, error_text):
    print(error_text)
    exit(error_code)
    
def ssl_connection(target, target_port):
    """
    Initiate a connection to the target site and try to get the certificate.
    The returned cert has a number of dictionary key/values to play with.
    Last line sends a SMTP email.
    """
    context = ssl.create_default_context()
    conn = context.wrap_socket(socket.socket(socket.AF_INET), server_hostname=target)
    conn.connect((target, target_port))
    cert = conn.getpeercert()
    print('Certificate valid from: ' + cert['notBefore'])
    print('Certificate expires: ' + cert['notAfter'])
    print('Number of days until cert expires: %s' % check_expiry_date(cert))
    print('\nAnd here is the whole thing.\n')
    pprint.pprint(cert)
    body = 'Subject: The cert on %s expires in %s days\n' % (target, check_expiry_date(cert))
    print(body)
    send_email(str(body))
    
def main():   
    try:
        ssl_connection(args.host, args.port)
    except ssl.SSLError as e:
        exit_error(1, e)
    except socket.gaierror as e:
        exit_error(1, e)
        
def check_expiry_date(cert):
    try:
        expires_on = datetime.strptime(cert['notAfter'], "%b %d %H:%M:%S %Y %Z")
    except:
        exit_error(1, "Sorry, can't see when the cert expires")
    expires_calc = expires_on - datetime.now()
    if expires_calc:
        return expires_calc.days
    else:
        return False

if __name__ == '__main__':
    main()
