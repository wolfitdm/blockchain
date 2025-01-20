from blockchain.common.utils import text_to_bytes, bytes_to_text
from blockchain.common.hash import hash
from blockchain.common.config import config

import os
import sys
import json
app_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = "C:/Users/ABC/Downloads/ZeroNet-win-dist-win64/ZeroNet-win-dist-win64/core"
app_dir = os.path.join(app_dir, "../core")
#os.chdir(app_dir)  # Change working dir to zeronet.py dir
sys.path.insert(0, os.path.join(app_dir, "src/lib"))  # External liblary directory
sys.path.insert(0, os.path.join(app_dir, "src"))  # Imports relative to src

from lib import pybitcointools as btctools

class Key:
    privkey = ''
    pubkey = ''

    def __init__(self, name, pubkey, privkey, key_file_path, address):
        self.name          = name
        self.pubkey        = pubkey
        self.privkey       = privkey
        self.key_file_path = key_file_path
        self.address       = address
        self.key_format    = config.get('key_format')

    def __prepare_data_for_signing(self, data):
        if isinstance(data, str):
            data = text_to_bytes(data)
        return hash(data)

    def sign(self, unsigned_data):
        return btctools.ecdsa_sign(unsigned_data, self.privkey)

    def verify(self, unsigned_data, signature):
        return btctools.ecdsa_verify(unsigned_data, signature, self.pubkey)

    def get_public_key(self):
        return self.pubkey
        
    def get_priv_key(self):
        return self.privkey
        
    def get_address(self):
        return self.address
        
    def write_to_file(self):
        data = {}
        if self.name:
           data["name"] = self.name
        if self.pubkey:
           data["pubkey"] = self.pubkey
        if self.privkey:
           data["privkey"] = self.privkey
        if self.key_file_path:
           data["key_file_path"] = self.key_file_path
        if self.address:
           data["address"] = self.address
        if self.key_format:
           data["key_format"] = self.key_format
        with open(self.key_file_path, 'w') as f:
             json.dump(data, f)

    def __repr__(self):
        return '{} {}'.format(self.name, self.address)