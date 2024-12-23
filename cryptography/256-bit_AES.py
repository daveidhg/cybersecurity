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


parser = argparse.ArgumentParser(description='Encrypt and decrypt texts or text files using AES')
parser.add_argument('-e', '--encrypt', help='Encrypt the text', action='store_true')
parser.add_argument('-d', '--decrypt', help='Decrypt the text', action='store_true')
parser.add_argument('-f', '--file', help='File to encrypt or decrypt')
parser.add_argument('-k', '--key', help='Key to use for encryption and decryption')
parser.add_argument('-o', '--output', help='Output file to write the encrypted or decrypted text. If not specified, the input file will be overwritten')
parser.add_argument('-t', '--text', help='Text to encrypt or decrypt')
parser.add_argument('-p', '--print', help='Print the encrypted or decrypted text', action='store_true')
parser.add_argument('-s', '--start', help='Open the file in the default text editor', action='store_true')
parser.add_argument('-c', '--copy', help='Copy the encrypted or decrypted text to the clipboard', action='store_true')
parser.add_argument('-v', '--version', action='version', version='%(prog)s 1.0')
args = parser.parse_args()

if not args.file and not args.text:
    parser.error('Please specify the file or text to encrypt or decrypt')
if args.file and args.text:
    parser.error('Please specify only one of file or text')
if not args.encrypt and not args.decrypt:
    parser.error('Please specify whether to encrypt or decrypt the text')
if args.encrypt and args.decrypt:
    parser.error('Please specify only one of encrypt or decrypt')
if not args.key:
    parser.error('Please specify the key to use for encryption and decryption')

key = args.key
handler = AESHandler(key)

if args.file:
    with open(args.file, 'r') as file:
        text = file.read()
else:
    text = args.text

if args.encrypt:
    new_text = handler.encrypt_text(text)
else:
    new_text = handler.decrypt_text(text)

if args.print:
    print(new_text)

if args.output:
    with open(args.output, 'w') as file:
        file.write(new_text)
    if args.start: 
        os.startfile(args.output)
elif args.file:
    with open(args.file, 'w') as file:
        file.write(new_text)
    if args.start:
        os.startfile(args.file)

if args.copy:
    import pyperclip
    pyperclip.copy(new_text)
    
