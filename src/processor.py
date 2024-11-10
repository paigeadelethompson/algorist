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
from random import random
import aiohttp
import aiozmq
import pyaes
from tinydb import TinyDB, Query
import os

class ConfigDB:
    def __init__(self):
        if os.environ.get("CONFIG_DB_PATH") is None:
            raise Exception("CONFIG_DB_PATH not set")

        self.config_db_path = os.environ.get("CONFIG_DB_PATH")

        if os.access(self.config_db_path, os.W_OK):
            raise Exception("CONFIG_DB_PATH isn't writable")

        self.db = TinyDB(self.config_db_path)

        if len(self.db.search(Query().key == "pbkdf2_password")) <= 0:
            passwd = "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(32))
            salt = "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(32))
            iv = os.urandom(16)

            self.db.table("config").insert({"key": "pbkdf2_password", "value": passwd})
            self.db.table("config").insert({"key": "pbkdf2_salt", "value": salt})
            self.db.table("config").insert({"key": "aes_iv", "value": iv})

        salt = self.db.search(Query().key == "pbkdf2_salt").pop().get("value")
        passwd = self.db.search(Query().key == "pbkdf2_password").pop().get("value")
        iv = self.db.search(Query().key == "pbkdf2_salt").pop().get("value")

        iterations = 100000
        key = hashlib.pbkdf2_hmac('sha256', passwd, salt, iterations)

        self.encrypt = pyaes.Encrypter(pyaes.AESModeOfOperationCBC(key, iv))
        self.decrypt = pyaes.Decrypter(pyaes.AESModeOfOperationCBC(key, iv))

    async def save_root_api_key(self, key):
        self.db.remove(Query().key == "api_key")
        self.db.table("config").insert({"key": "api_key", "value": self.encrypt_data(key)})

    async def get_root_api_key(self):
        raise NotImplementedError()

    async def decrypt_data(self, encrypted_value):
        decrypted = self.decrypt.feed(encrypted_value)
        decrypted += self.decrypt.feed()
        return decrypted

    async def encrypt_data(self, unencrypted_value):
        encrypted = self.encrypt.feed(unencrypted_value)
        encrypted += self.encrypt.feed()
        return encrypted

class TornV2API(aiozmq.rpc.AttrHandler):
    def __init__(self, db: ConfigDB):
        self._base_url = "https://api.torn.com/v2"
        self.db = db

    '''
    Documentation:
    https://www.torn.com/swagger/index.html#/User/get_user
    '''
    @aiozmq.rpc.method
    async def get_user(self, id: int, api_key=None):
        if api_key is None:
            query = "{base}/user?key={api_key}&id={id}&striptags=true".format(
            base=self._base_url, api_key=self.db.get_root_api_key(), id=id)
        else:
            key = self.db.decrypt_data(api_key)
            query = "{base}/user?key={api_key}&id={id}&striptags=true".format(
                base=self._base_url, api_key=key, id=id)

        async with aiohttp.request('GET', query) as resp:
            assert resp.status == 200
            response = await resp
            client = await aiozmq.rpc.connect_rpc(
                connect=os.environ.get("RESPONSE_PROCESSOR_BIND_HOST"))
            await client.call.user_api_response(response)
            await client.close()

    @aiozmq.rpc.method
    async def encrypt_user_api_key(self, user_api_key):
        return self.db.encrypt_data(user_api_key)

async def inbox():
    config = ConfigDB()
    if os.environ.get("REQUEST_PROCESSOR_BIND_HOST") is None:
        raise Exception("REQUEST_PROCESSOR_BIND_HOST not set")
    bind_host = os.environ.get("REQUEST_PROCESSOR_BIND_HOST")
    server = await aiozmq.rpc.serve_rpc(TornV2API(config), bind=bind_host)
    server_addr = list(server.transport.bindings()).pop(0)
    await server.wait_closed()