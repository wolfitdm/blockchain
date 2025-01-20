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

from blockchain.common.utils import text_to_bytes

def hash(data):
    return btctools.bin_sha256(data)

def hash_to_hex(data):
    return btctools.sha256(data)

def hash_string(text):
    return hash(text_to_bytes(text))

def hash_string_to_hex(text):
    return hash_to_hex(text_to_bytes(text))
