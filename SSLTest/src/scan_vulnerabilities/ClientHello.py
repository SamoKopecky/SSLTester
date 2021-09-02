import secrets

from struct import pack

from .utils import version_conversion


class ClientHello:
    def __init__(self, version, cipher_suites=None, fill_cipher_suites=True):
        self.version = version
        self.record_protocol = bytearray([
            0x16,  # Content type (Handshake)
            0x03, self.version,  # Version
            # 0x00, 0x00,  Length
        ])
        self.handshake_protocol_header = bytearray([
            0x01,  # Handshake type
            # 0x00, 0x00, 0x00,  Length
        ])
        self.handshake_protocol = bytearray([
            0x03, self.version,  # TLS version
            # Random bytes
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00,  # Session id length
        ])
        # Fill random bytes
        self.handshake_protocol[2:34] = secrets.token_bytes(32)
        self.cipher_suites = self.get_cipher_suite_bytes(cipher_suites, fill_cipher_suites)
        self.compression = bytearray([
            0x01,  # Compression method length
            0x00  # Compression method
        ])
        self.extensions = bytearray([
            # 0x00, 0x00,  Extensions length
            # Supported groups
            0x00, 0x0a, 0x00, 0x0c, 0x00, 0x0a, 0x00, 0x1d,
            0x00, 0x17, 0x00, 0x1e, 0x00, 0x19, 0x00, 0x18,
            # Signature algorithm
            0x00, 0x0d, 0x00, 0x2a, 0x00, 0x28, 0x04, 0x03,
            0x05, 0x03, 0x06, 0x03, 0x08, 0x07, 0x08, 0x08,
            0x08, 0x09, 0x08, 0x0a, 0x08, 0x0b, 0x08, 0x04,
            0x08, 0x05, 0x08, 0x06, 0x04, 0x01, 0x05, 0x01,
            0x06, 0x01, 0x03, 0x03, 0x03, 0x01, 0x03, 0x02,
            0x04, 0x02, 0x05, 0x02, 0x06, 0x02,
        ])

    def construct_client_hello(self):
        """
        Concat all the client hello parts

        :return: Client hello bytes
        :rtype: bytearray
        """
        # Body of the client hello
        extensions_length = pack('>H', len(self.extensions))
        client_hello = self.handshake_protocol + self.cipher_suites + self.compression
        client_hello += extensions_length + self.extensions

        # Handshake protocol header
        length = pack('>I', len(client_hello))[1:]
        client_hello = self.handshake_protocol_header + length + client_hello

        # Record protocol
        length = pack('>H', len(client_hello))
        client_hello = self.record_protocol + length + client_hello
        return client_hello

    def get_cipher_suite_bytes(self, more_cipher_suites, fill_cipher_suites):
        """
        Choose cipher suites based on the protocol version

        :param bool fill_cipher_suites:
        :param bytes or bytearray more_cipher_suites: Additional cipher suites
        :return: Chosen ciphers
        :rtype: bytearray
        """
        cipher_suites = bytearray()
        if more_cipher_suites is not None:
            cipher_suites += more_cipher_suites
        str_version = version_conversion(self.version, False)
        # TODO: fix
        if fill_cipher_suites:
            if 'SSLv3' == str_version:
                cipher_suites += bytearray([
                    0xc0, 0x14, 0xc0, 0x0a, 0x00, 0x39, 0x00, 0x38,
                    0x00, 0x37, 0x00, 0x36, 0x00, 0x88, 0x00, 0x87,
                    0x00, 0x86, 0x00, 0x85, 0xc0, 0x0f, 0xc0, 0x05,
                    0x00, 0x35, 0x00, 0x84, 0xc0, 0x13, 0xc0, 0x09,
                    0x00, 0x33, 0x00, 0x32, 0x00, 0x31, 0x00, 0x30,
                    0x00, 0x9a, 0x00, 0x99, 0x00, 0x98, 0x00, 0x97,
                    0x00, 0x45, 0x00, 0x44, 0x00, 0x43, 0x00, 0x42,
                    0xc0, 0x0e, 0xc0, 0x04, 0x00, 0x2f, 0x00, 0x96,
                    0x00, 0x41, 0x00, 0x07, 0xc0, 0x11, 0xc0, 0x07,
                    0xc0, 0x0c, 0xc0, 0x02, 0x00, 0x05, 0x00, 0x04,
                    0xc0, 0x12, 0xc0, 0x08, 0x00, 0x16, 0x00, 0x13,
                    0x00, 0x10, 0x00, 0x0d, 0xc0, 0x0d, 0xc0, 0x03,
                    0x00, 0x0a, 0x00, 0xff, 0xc0, 0x22, 0xc0, 0x21,
                    0xc0, 0x20, 0xc0, 0x19, 0x00, 0x3a, 0x00, 0x89,
                    0x00, 0x8d, 0xc0, 0x1f, 0xc0, 0x1e, 0xc0, 0x1d,
                    0xc0, 0x18, 0x00, 0x34, 0x00, 0x9b, 0x00, 0x46,
                    0x00, 0x8c, 0xc0, 0x16, 0x00, 0x18, 0x00, 0x8a,
                    0xc0, 0x1c, 0xc0, 0x1b, 0xc0, 0x1a, 0xc0, 0x17,
                    0x00, 0x1b, 0x00, 0x8b, 0xc0, 0x10, 0xc0, 0x06,
                    0xc0, 0x15, 0xc0, 0x0b, 0xc0, 0x01, 0x00, 0x02,
                    0x00, 0x01
                ])
            elif 'TLSv1.1' == str_version or 'TLSv1.0' == str_version:
                cipher_suites += bytearray([
                    0xc0, 0x0a, 0xc0, 0x14, 0x00, 0x39, 0x00, 0x38,
                    0x00, 0x88, 0x00, 0x87, 0xc0, 0x19, 0x00, 0x3a,
                    0x00, 0x89, 0xc0, 0x09, 0xc0, 0x13, 0x00, 0x33,
                    0x00, 0x32, 0x00, 0x9a, 0x00, 0x99, 0x00, 0x45,
                    0x00, 0x44, 0xc0, 0x18, 0x00, 0x34, 0x00, 0x9b,
                    0x00, 0x46, 0x00, 0x35, 0x00, 0x84, 0x00, 0x2f,
                    0x00, 0x96, 0x00, 0x41, 0x00, 0xff
                ])
            elif 'TLSv1.2' == str_version:
                cipher_suites += bytearray([
                    0xc0, 0x2c, 0xc0, 0x30, 0x00, 0xa3, 0x00, 0x9f,
                    0xcc, 0xa9, 0xcc, 0xa8, 0xcc, 0xaa, 0xc0, 0xaf,
                    0xc0, 0xad, 0xc0, 0xa3, 0xc0, 0x9f, 0xc0, 0x5d,
                    0xc0, 0x61, 0xc0, 0x57, 0xc0, 0x53, 0x00, 0xa7,
                    0xc0, 0x2b, 0xc0, 0x2f, 0x00, 0xa2, 0x00, 0x9e,
                    0xc0, 0xae, 0xc0, 0xac, 0xc0, 0xa2, 0xc0, 0x9e,
                    0xc0, 0x5c, 0xc0, 0x60, 0xc0, 0x56, 0xc0, 0x52,
                    0x00, 0xa6, 0xc0, 0x24, 0xc0, 0x28, 0x00, 0x6b,
                    0x00, 0x6a, 0xc0, 0x73, 0xc0, 0x77, 0x00, 0xc4,
                    0x00, 0xc3, 0x00, 0x6d, 0x00, 0xc5, 0xc0, 0x23,
                    0xc0, 0x27, 0x00, 0x67, 0x00, 0x40, 0xc0, 0x72,
                    0xc0, 0x76, 0x00, 0xbe, 0x00, 0xbd, 0x00, 0x6c,
                    0x00, 0xbf, 0xc0, 0x0a, 0xc0, 0x14, 0x00, 0x39,
                    0x00, 0x38, 0x00, 0x88, 0x00, 0x87, 0xc0, 0x19,
                    0x00, 0x3a, 0x00, 0x89, 0xc0, 0x09, 0xc0, 0x13,
                    0x00, 0x33, 0x00, 0x32, 0x00, 0x9a, 0x00, 0x99,
                    0x00, 0x45, 0x00, 0x44, 0xc0, 0x18, 0x00, 0x34,
                    0x00, 0x9b, 0x00, 0x46, 0x00, 0x9d, 0xc0, 0xa1,
                    0xc0, 0x9d, 0xc0, 0x51, 0x00, 0x9c, 0xc0, 0xa0,
                    0xc0, 0x9c, 0xc0, 0x50, 0x00, 0x3d, 0x00, 0xc0,
                    0x00, 0x3c, 0x00, 0xba, 0x00, 0x35, 0x00, 0x84,
                    0x00, 0x2f, 0x00, 0x96, 0x00, 0x41, 0x00, 0xff
                ])
        return pack('>H', len(cipher_suites)) + cipher_suites
