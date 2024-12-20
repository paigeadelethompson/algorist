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
import zerorpc
from tinydb import TinyDB
from algorist.content import module_logger

class ContentConfigDB:
    def __init__(self, request_processor_bind_host, config_db_path):
        self.config_db_path = config_db_path
        self.request_processor_bind_host = request_processor_bind_host
        self.db = TinyDB("{}/config.db".format(self.config_db_path))
        module_logger.info("loaded content service configuration database")


    def store_default_api_key(self, api_key):
        client = zerorpc.Client()
        client.connect(self.request_processor_bind_host)
        encrypted_api_key = client.encrypt_api_key(api_key)
        if len(self.db.table("default_api_key").all()) > 0:
            self.db.table("default_api_key").truncate()
            self.db.table("default_api_key").remove()
        self.db.table("default_api_key").insert({"value": encrypted_api_key})

    def get_default_api_key(self):
        if len(self.db.table("default_api_key").all()) <= 0:
            raise Exception("No default api key is set")
        ret = self.db.table("default_api_key").all().pop().get("value")
        return ret