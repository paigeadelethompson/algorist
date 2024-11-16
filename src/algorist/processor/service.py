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

import traceback
from base64 import b64encode, b64decode
import requests
from algorist.processor.config import ConfigDB
from algorist.processor import module_logger

class TornV2API(object):
    def __init__(self, db: ConfigDB):
        module_logger.info("creating TornV2API request service")
        self._base_url = "https://api.torn.com/v2"
        self.db = db

    def get_user(self, api_key, id: str):
        try:
            key = self.db.decrypt_data(b64decode(api_key))
            query = "{base}/user?key={api_key}&id={id}&striptags=true".format(
                base=self._base_url, api_key=key, id=id)
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

