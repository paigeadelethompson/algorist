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

import json
import traceback
import zerorpc
from tinydb import TinyDB
from algorist.content.config import ContentConfigDB
from algorist.content.user.hof import UserHOF
from algorist.content.user.user import User
from algorist.content.user import module_logger

class UserDB:
    def __init__(self, request_processor_bind_host, config_db, user_db_path):
        self.config_db = config_db
        self.root_db_path = user_db_path
        self.request_processor_bind_host = request_processor_bind_host
        module_logger.info("UserDB manager instantiated")

    def _get_db(path) -> TinyDB:
        return TinyDB(path)

    def get_user(self, id: int):
        try:
            client = zerorpc.Client()
            client.connect(self.request_processor_bind_host)
            key = self.config_db.get_default_api_key()
            payload = client.get_user(key, id)
            if payload is None:
                raise Exception("empty response")
            u = User(json.loads(payload))
            if u.is_error():
                raise Exception(u.payload.get("error"))
            self.save_user(u)
            path = "/{path}/{id}".format(path=self.root_db_path, id=u.id())
            db = UserDB._get_db(path)
            return [User(index) for index in db.table("user_objects").all()]
        except Exception as e:
            traceback.print_exception(e)
            return []

    def save_user(self, user: User):
        try:
            path = "/{path}/{id}".format(path=self.root_db_path, id=user.id())
            db = UserDB._get_db(path)
            db.table("user_objects").insert(user.payload)
        except Exception as e:
            traceback.print_exception(e)

    def save_user_hof(self, user_hof: UserHOF):
        raise NotImplementedError()