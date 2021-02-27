import ssl
import socket
import re
from OpenSSL import SSL
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from ..utils import convert_openssh_to_iana
from ..exceptions.UnknownConnectionError import UnknownConnectionError
from ..exceptions.ConnectionTimeoutError import ConnectionTimeoutError
from ..exceptions.DNSError import DNSError


def get_website_info(hostname, port):
    """
    Gathers objects to be rated.

    Uses functions in this module to create a connection and get the
    servers certificate, cipher suite and protocol used in the connection.
    :param port: port to scan on
    :param hostname: hostname of the webserver
    :return:
        certificate -- used certificate to verify the server
        cipher_suite -- negotiated cipher suite
        protocol -- protocol name and version
    """
    if '/' in hostname:
        hostname = fix_hostname(hostname)
    ssl_socket = create_session(hostname, port)
    cipher_suite, protocol = get_cipher_suite_and_protocol(ssl_socket)
    certificate = get_certificate(ssl_socket)
    ssl_socket.close()
    return certificate, cipher_suite, protocol


def get_certificate(ssl_socket):
    """
    Gathers a certificate in a der format.

    :param ssl_socket: secured socket
    :return: gathered certificate
    """
    certificate_pem = bytes(ssl_socket.getpeercert(binary_form=True))
    return x509.load_der_x509_certificate(certificate_pem, default_backend())


def get_cipher_suite_and_protocol(ssl_socket):
    """
    Gathers the cipher suite and the protocol from the ssl_socket.

    :param ssl_socket: secure socket
    :return: negotiated cipher suite and the protocol
    """
    cipher_suite = ssl_socket.cipher()[0]
    if '-' in cipher_suite:
        try:
            cipher_suite = convert_openssh_to_iana(cipher_suite)
        except Exception as e:
            print(e)
    return cipher_suite, ssl_socket.version()


def create_session_pyopenssl(hostname, port, context):
    """
    Creates a secure connection to any server on any port with a defined context.

    This function creates a secure connection with pyopenssl lib. Original ssl lib
    doesn't work with older TLS versions on some OpenSSL implementations and thus
    the program can't scan for all supported versions.
    :param hostname: hostname of the website
    :param context: ssl context
    :param port: port
    :return: created secure socket
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ssl_socket = SSL.Connection(context, sock)
    ssl_socket.connect((hostname, port))
    ssl_socket.do_handshake()
    return ssl_socket


def create_session(hostname, port, context=ssl.create_default_context()):
    """
    Creates a secure connection to any server on any port with a defined context
    on a specific timeout.

    :param hostname: hostname of the website
    :param context: ssl context
    :param port: port
    :return: created secure socket
    """
    if hostname == '192.168.1.220':
        context.check_hostname = False
        context.verify_mode = ssl.VerifyMode.CERT_NONE
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)  # in seconds
    ssl_socket = context.wrap_socket(sock, server_hostname=hostname)
    try:
        ssl_socket.connect((hostname, port))
    except socket.timeout:
        raise ConnectionTimeoutError()
    except socket.gaierror:
        raise DNSError()
    except socket.error as e:
        raise UnknownConnectionError(e)
    return ssl_socket


def fix_hostname(hostname):
    """
    Extracts the domain name.

    :param hostname: hostname address to be checked
    :return: fixed hostname address
    """
    print('Correcting url...')
    if hostname[:4] == 'http':
        # Removes http(s):// and anything after TLD (*.com)
        hostname = re.search('[/]{2}([^/]+)', hostname).group(1)
    else:
        # Removes anything after TLD (*.com)
        hostname = re.search('^([^/]+)', hostname).group(0)
    print('Corrected url: {}'.format(hostname))
    return hostname
