from ..VulnerabilityTest import VulnerabilityTest
from ...scan_parameters.connections.ClientHello import ClientHello
from ...utils import send_data_return_sock, is_server_hello, filter_cipher_suite_bytes


class RC4Support(VulnerabilityTest):
    test_name = 'RC4 Support'

    def __init__(self, supported_protocols, address, timeout, protocol):
        super().__init__(supported_protocols, address, timeout, protocol)
        self.valid_protocols = ['TLSv1.2', 'TLSv1.1', 'TLSv1.0', 'SSLv3']
        if 'TLSv1.0' in self.supported_protocols and 'TLSv1.1' in supported_protocols:
            self.valid_protocols.remove('TLSv1.1')
        self.scan_once = False

    def test(self, version):
        """
        Scan for rc4 cipher support

        :param int version: SSL/TLS version
        :return: Whether the server is vulnerable
        :rtype: bool
        """
        cipher_suite_bytes = ClientHello.get_cipher_suites_for_version(version)
        rc4_cipher_suites = filter_cipher_suite_bytes(cipher_suite_bytes, lambda cs: 'RC4' in cs)
        client_hello = ClientHello(version, rc4_cipher_suites, False).construct_client_hello()
        response, sock = send_data_return_sock(self.address, client_hello, self.timeout, self.test_name)
        sock.close()
        if not is_server_hello(response):
            return False
        # 0x02 means fatal error and 0x28 means handshake failure
        if response[-2] == 0x02 and response[-1] == 0x28:
            return False
        else:
            return True
