from Crypto.Random import get_random_bytes
import base64
import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import argparse
import os

class AESHandler(object):
    def __init__(self, key):
        self.bs = AES.block_size
        self.key = hashlib.sha256(key.encode()).digest()

    def encrypt_text(self, raw):
        raw = pad(raw.encode(), self.bs)
        iv = get_random_bytes(self.bs)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw)).decode('utf-8')
    
    def decrypt_text(self, enc):
        enc = base64.b64decode(enc)
        iv = enc[:self.bs]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return unpad(cipher.decrypt(enc[self.bs:]), self.bs).decode('utf-8')


parser = argparse.ArgumentParser(description='Encrypt and decrypt text files using AES')
parser.add_argument('-e', '--encrypt', help='Encrypt the text', action='store_true')
parser.add_argument('-d', '--decrypt', help='Decrypt the text', action='store_true')
parser.add_argument('-f', '--file', help='File to encrypt or decrypt')
parser.add_argument('-k', '--key', help='Key to use for encryption and decryption')
args = parser.parse_args()

if not args.encrypt and not args.decrypt:
    parser.error('Please specify whether to encrypt or decrypt the text')
if args.encrypt and args.decrypt:
    parser.error('Please specify only one of encrypt or decrypt')
if not args.file:
    parser.error('Please specify the file to encrypt or decrypt')
if not args.key:
    parser.error('Please specify the key to use for encryption and decryption')

key = args.key
handler = AESHandler(key)
file = args.file
with open(file, "r+") as f:
    text = f.read()
    f.seek(0)
    if args.encrypt:
        encrypted = handler.encrypt_text(text)
        f.write(encrypted)
    elif args.decrypt:
        decrypted = handler.decrypt_text(text)
        f.write(decrypted)
    f.truncate()

os.startfile(file)
