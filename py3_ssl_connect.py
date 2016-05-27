# Simple Python 3 script to connect to a specified site and output whatever dict values are returned.
# In this example the output is: valid from, valid until, full dict, and number of days until expiry.
# This will be the basis of a cron job to send an email notification if a cert expires within x days.
# To-do:  better error checking, make it less gullible.

import ssl
import socket
import argparse
import pprint
from datetime import datetime

parser = argparse.ArgumentParser(description='Specify a site to connect to.')
parser.add_argument('host', help='Add the name of the site you want to connect to')
parser.add_argument('-p', '--port', help='Specify a port to connect to', type=int, default=443)
args=parser.parse_args()

if args.host and args.port:
    print( '#' * 20 + '\n' + 'Trying to connect to:  %s:%s \n' % (args.host,args.port))
    
def exit_error(error_code, error_text):
    print(error_text)
    exit(error_code)
    
def ssl_connection(target, target_port):
    """
    Initiate a connection to the target site and try to get the certificate.
    The returned cert has a number of dictionary key/values to play with.
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
