"""
Copyright (c) 2024 Paige Thompson (paige@paige.bio)

Permission is hereby granted, free of charge, to any person
obtaining a copy of this software and associated documentation
files (the "Software"), to deal in the Software without
restriction, including without limitation the rights to use,
copy, modify, merge, publish, distribute, sublicense, and/or
sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.
"""

import os
from base64 import b64encode, b64decode
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad, pad
from pbkdf2 import PBKDF2
from tinydb import TinyDB

class ConfigDB:
    def __init__(self, config_db_path):
        self.config_db_path = config_db_path
        self.db = TinyDB("{}/config.db".format(self.config_db_path))
        if len(self.db.table("pbkdf2_key").all()) <= 0:
            passwd = os.urandom(32)
            salt = os.urandom(32)
            iv = b64encode(os.urandom(16)).decode('utf-8')
            key = b64encode(PBKDF2(passwd, salt).read(32)).decode('utf-8')
            self.db.table("aes_iv").insert({"value": iv})
            self.db.table("encryption_key").insert({"value": key})
        self.iv = b64decode(self.db.table("aes_iv").all().pop().get("value"))
        self.key = b64decode(self.db.table("encryption_key").all().pop().get("value"))

    def decrypt_data(self, encrypted_value):
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        decrypted_text = cipher.decrypt(encrypted_value)
        unpadded_text = unpad(decrypted_text, AES.block_size)
        return unpadded_text.decode('utf-8')

    def encrypt_data(self, unencrypted_value):
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        padded_plaintext = pad(unencrypted_value.encode(), AES.block_size)
        ciphertext = cipher.encrypt(padded_plaintext)
        return ciphertext
