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

import hashlib
import string
from random import random, choice
import aiohttp
import aiozmq
from aiozmq import rpc
import pyaes
from tinydb import TinyDB, Query
import os
from base64 import b64encode, b64decode


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

            iv = b64encode(os.urandom(16))
            key = b64encode(hashlib.pbkdf2_hmac('sha256', passwd, salt, iterations=100000))

            self.db.table("aes_iv").insert({"value": iv})
            self.db.table("encryption_key").insert({"value": key})

        iv = b64decode(self.db.table("aes_iv").all().pop().get("value"))
        key = b64decode(self.db.table("encryption_key").all().pop().get("value"))

        self.encrypt = pyaes.Encrypter(pyaes.AESModeOfOperationCBC(key, b64decode(iv)))
        self.decrypt = pyaes.Decrypter(pyaes.AESModeOfOperationCBC(key, b64decode(iv)))

    async def decrypt_data(self, encrypted_value):
        decrypted = self.decrypt.feed(encrypted_value)
        decrypted += self.decrypt.feed()
        return decrypted

    async def encrypt_data(self, unencrypted_value):
        encrypted = self.encrypt.feed(unencrypted_value)
        encrypted += self.encrypt.feed()
        return encrypted


class TornV2API(rpc.AttrHandler):
    def __init__(self, db: ConfigDB):
        self._base_url = "https://api.torn.com/v2"
        self.db = db

    @aiozmq.rpc.method
    async def get_user(self, id: int, api_key):
        key = self.db.decrypt_data(b64decode(api_key))
        query = "{base}/user?key={api_key}&id={id}&striptags=true".format(
            base=self._base_url, api_key=key, id=id)
        async with aiohttp.request('GET', query) as response:
            if (response.status == 200
                    and response.content_length is not None
                    and response.content_length <= 1048576):
                return await response.content.read(response.content_length)
            else:
                return None

    @aiozmq.rpc.method
    async def encrypt_api_key(self, user_api_key):
        return b64encode(self.db.encrypt_data(user_api_key))


async def inbox():
    config = ConfigDB()
    if os.environ.get("REQUEST_PROCESSOR_BIND_HOST") is None:
        raise Exception("REQUEST_PROCESSOR_BIND_HOST not set")
    bind_host = os.environ.get("REQUEST_PROCESSOR_BIND_HOST")
    server = await aiozmq.rpc.serve_rpc(TornV2API(config), bind=bind_host)
    await server.wait_closed()
