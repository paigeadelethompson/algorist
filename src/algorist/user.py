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
import os
from tinydb import TinyDB
from tinydb.table import Document

from algorist.sandbox.config import SandBoxConfigDB
import traceback
import zerorpc
from datetime import datetime

class User:
    def __init__(self, payload: dict | Document):
        self.payload = payload
        if self.payload.get("snapshot") is None:
            self.payload["snapshot"] = str(datetime.now())

    def is_error(self):
        if self.payload.get("error") is not None:
            return True
        return False

    def error_message(self):
        raise NotImplementedError()

    def error_code(self):
        raise NotImplementedError()

    def id(self):
        return self.payload.get("player_id")

    def name(self):
        return self.payload.get("name")

    def u_lvl(self):
        return self.payload.get("level")

    def cur_hp(self):
        return self.payload.get(
            "life").get(
            "current")

    def max_hp(self):
        return self.payload.get(
            "life").get(
            "maximum")

    def stat_desc(self):
        return self.payload.get(
            "status").get(
            "description")

    def snapshot(self):
        return datetime(self.payload.get("snapshot"))


class UserHOF:
    """
    When requesting selection with Limited,
    Full or Custom key, battle_stats selection will be populated.
    """
    def __init__(self, user, payload):
        self._user = user
        self.payload = payload

    def attacks(self):
        return {
            "v": self.get("attacks").get("value"),
            "r": self.get("attacks").get("rank")
        }

    def defense(self):
        return {
            "v": self.get("defends").get("value"),
            "r": self.get("defends").get("rank")
        }

    def hof_lvl(self):
        return {
            "v": self.get("level").get("value"),
            "r": self.get("level").get("rank")
        }

class UserDB:
    def __init__(self):
        self.config_db_path = None
        if os.environ.get("USER_DB_PATH") is None:
            raise Exception("USER_DB_PATH not set")
        self.path = os.environ.get("USER_DB_PATH")
        if not os.path.isdir(self.path):
            raise Exception("USER_DB_PATH should be a directory")
        if not os.access(self.path, os.W_OK):
            raise Exception("USER_DB_PATH isn't writable")

    def _get_db(path) -> TinyDB:
        return TinyDB(path)

    def get_user(self, id: int):
        try:
            client = zerorpc.Client()
            client.connect(os.environ.get("REQUEST_PROCESSOR_BIND_HOST"))
            key = SandBoxConfigDB().get_default_api_key()
            payload = client.get_user(key, id)
            if payload is None:
                raise Exception("empty response")
            u = User(json.loads(payload))
            if u.is_error():
                raise Exception(u.payload.get("error"))
            self.save_user(u)
            path = "{path}/{id}".format(path=self.path, id=u.id())
            db = UserDB._get_db(path)
            return [User(index) for index in db.table("user_objects").all()]
        except Exception as e:
            traceback.print_exception(e)
            return []

    def save_user(self, user: User):
        try:
            path = "{path}/{id}".format(path=self.path, id=user.id())
            db = UserDB._get_db(path)
            db.table("user_objects").insert(user.payload)
        except Exception as e:
            traceback.print_exception(e)

    def save_user_hof(self, user_hof: UserHOF):
        raise NotImplementedError()