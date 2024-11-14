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

from pbkdf2 import PBKDF2
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import zerorpc
import requests
from tinydb import TinyDB
import os
from base64 import b64encode, b64decode
import traceback

class ConfigDB:
    def __init__(self):
        if os.environ.get("CONFIG_DB_PATH") is None:
            raise Exception("CONFIG_DB_PATH not set")
        self.config_db_path = os.environ.get("CONFIG_DB_PATH")
        if not os.access(self.config_db_path, os.W_OK):
            raise Exception("CONFIG_DB_PATH isn't writable")
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

class TornV2API(object):
    def __init__(self, db: ConfigDB):
        self._base_url = "https://api.torn.com/v2"
        self.db = db

    def get_user(self, api_key, id: str):
        try:
            key = self.db.decrypt_data(b64decode(api_key))
            print(key)
            query = "{base}/user?key={api_key}&id={id}&striptags=true".format(
                base=self._base_url, api_key=key, id=id)
            print(query)
            with requests.request('GET', query) as response:
                if response.status_code == 200:
                    return response.content
                else:
                    return None
                    raise NotImplementedError("http status code {}".format(response.status_code))

        except Exception as e:
            traceback.print_exception(e)

    def encrypt_api_key(self, user_api_key):
        try:
            return b64encode(self.db.encrypt_data(user_api_key)).decode('utf-8')
        except Exception as e:
            traceback.print_exception(e)


async def inbox():
    config = ConfigDB()
    if os.environ.get("REQUEST_PROCESSOR_BIND_HOST") is None:
        raise Exception("REQUEST_PROCESSOR_BIND_HOST not set")
    bind_host = os.environ.get("REQUEST_PROCESSOR_BIND_HOST")
    server = zerorpc.Server(TornV2API(config))
    server.bind(bind_host)
    server.run()
