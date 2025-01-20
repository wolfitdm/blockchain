import os
import sys
import json

from base64 import b64encode

app_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = "C:/Users/ABC/Downloads/ZeroNet-win-dist-win64/ZeroNet-win-dist-win64/core"
app_dir = os.path.join(app_dir, "../core")
#os.chdir(app_dir)  # Change working dir to zeronet.py dir
sys.path.insert(0, os.path.join(app_dir, "src/lib"))  # External liblary directory
sys.path.insert(0, os.path.join(app_dir, "src"))  # Imports relative to src

from lib import pybitcointools as btctools

import os.path
from glob import glob
from blockchain.common.key import Key
from blockchain.common.hash import hash_to_hex
from blockchain.common.config import config
from blockchain.common.utils import text_to_bytes

MAX_KEY_NAME_LENGTH = 256

class Crypto:
    def __init__(self):
        self.key_store_dir = config.get('key_store_dir')
        self.key_format    = config.get('key_format')
        self.key_size      = config.get('key_size')

    @staticmethod
    def validate_signature(data, public_key, signature):
        #public_key = RSA.importKey(public_key)
        return Key(None, public_key, None, None, None).verify(data, signature)

    @staticmethod
    def validate_transaction(transaction):
        signature = transaction.signature
        public_key = transaction.public_key
        transaction_details = transaction.get_details_for_signature()
        return Crypto.validate_signature(transaction_details, public_key, signature)

    def __get_address_for_key(self, key):
        return btctools.privkey_to_address(key)

    def get_key(self, key_name):
        file_path = self.__get_key_file_path(key_name)
        if os.path.isfile(file_path):
            with open(file_path, 'r') as f:
                 data = json.load(f)
                 if not "name" in data or data["name"] != key_name:
                    data["name"] = key_name
                 if not "key_file_path" in data or data["key_file_path"] != file_path:
                    data["key_file_path"] = file_path
                 address = self.__get_address_for_key(data["privkey"])
                 if not "address" in data or data["address"] != address:
                    data["address"] = address
                 return Key(data["name"], data["pubkey"], data["privkey"], data["key_file_path"], data["address"])

    def get_key_by_address(self, key_address):
        for key in self.get_keys():
            if key.address == key_address:
               return key

    def get_keys(self):
        keys = []
        for file_path in glob(os.path.join(self.key_store_dir, '*.{}'.format(self.key_format))):
            with open(file_path, 'rb') as f:
                key_name = self.__get_key_name_from_file(f)
                keys.append(self.get_key(key_name))

        return keys

    def generate_key(self, key_name):
        print("sdss")
        if self.get_key(key_name):
            raise ValueError('a key called {} already exists'.format(key_name))

        if len(key_name) > MAX_KEY_NAME_LENGTH:
            raise ValueError('key name is too long, must be {} characters or less'.format(MAX_KEY_NAME_LENGTH))
        print("here")
        privkey = btctools.encode_privkey(btctools.random_key(), "wif")
        pubkey = btctools.privkey_to_pubkey(privkey)
        address = btctools.pubkey_to_address(pubkey)
        key_file_path = self.__get_key_file_path(key_name)
        newkey = Key(key_name, pubkey, privkey, key_file_path, address)
        newkey.write_to_file()

        return self.get_key(key_name)

    def __get_key_file_path(self, key_name):
        file_name = '{}.{}'.format(key_name, self.key_format)
        return os.path.join(self.key_store_dir, file_name)

    def __get_key_name_from_file(self, f):
        file_name_without_ext, _ = os.path.splitext(os.path.basename(f.name))
        return file_name_without_ext
