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
import sys, os
from tinydb import TinyDB, Query

class User:
    def __init__(self, payload: str):
        self.payload = json.loads(payload)

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

class UserHOF:
    """
    When requesting selection with Limited,
    Full or Custom key, battle_stats selection will be populated.
    """
    def __init__(self, user, payload):
        self._user = user
        self.payload = json.loads(payload)

    def att(self):
        return {
            "v": self.get("attacks").get("value"),
            "r": self.get("attacks").get("rank")
        }

    def gua(self):
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
        path = os.environ.get("USER_DB_PATH")
        if not os.path.isdir(path):
            raise Exception("USER_DB_PATH should be a directory")
        if os.access(path, os.W_OK):
            raise Exception("USER_DB_PATH isn't writable")

    async def get_db(path):
        return TinyDB(path)

    async def list_users(self):
        raise NotImplementedError()

    async def list_factions(self):
        raise NotImplementedError()

    async def get_user(self, id: int):
        path = "{path}/{id}".format(path=self.user_db_path, id=id)
        return UserDB.get_db(path)

    async def get_faction(self, id: int):
        path = "{path}/{id}".format(path=self.faction_db_path, id=id)
        return UserDB.get_db(path)

    async def save_user(self, user: User):
        raise NotImplementedError()

    async def save_user_hof(self, user_hof: UserHOF):
        raise NotImplementedError()