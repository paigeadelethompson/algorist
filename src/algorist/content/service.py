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
from algorist.content.config import ContentConfigDB
from algorist.content.user.database import UserDB


class ContentService:
    def __init__(self, request_processor_bind_host, config_db_path, user_db_path):
        self.config_db = ContentConfigDB(request_processor_bind_host, config_db_path)
        self.user_db = UserDB(request_processor_bind_host, self.config_db, user_db_path)

    def set_default_torn_api_key(self, api_key):
        try:
            self.config_db.store_default_api_key(api_key)
        except Exception as e:
            traceback.print_exception(e)

    def link_torn_user(self, torn_user_id, discord_user_id):
        try:
            raise NotImplementedError()
        except Exception as e:
            traceback.print_exception(e)

    def set_torn_api_key(self, api_key, discord_user_id):
        try:
            raise NotImplementedError()
        except Exception as e:
            traceback.print_exception(e)

    def get_torn_user(self, api_key, torn_user_id):
        try:
            raise NotImplementedError()
        except Exception as e:
            traceback.print_exception(e)

    def get_torn_faction(self, api_key, torn_faction_id):
        try:
            raise NotImplementedError()
        except Exception as e:
            traceback.print_exception(e)