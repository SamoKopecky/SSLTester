import json


def convert_openssh_to_iana(search_term):
    jfile = open('./resources/iana_openssl_cipher_mapping.json', 'r')
    jdata = json.loads(jfile.read())
    for row in jdata:
        if jdata[row] == search_term:
            return row
    raise IndexError("cipher is not contained in .json file")
