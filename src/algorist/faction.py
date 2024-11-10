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

class Faction:
    def __init__(self, payload, api_key=None):
        self.payload = json.loads(payload)

class FactionDB:
    def __init__(self):
        self.config_db_path = None
        if os.environ.get("FACTION_DB_PATH") is None:
            raise Exception("FACTION_DB_PATH not set")

        path = os.environ.get("FACTION_DB_PATH")

        if not os.path.isdir(path):
            raise Exception("FACTION_DB_PATH should be a directory")
        if os.access(path, os.W_OK):
            raise Exception("FACTION_DB_PATH isn't writable")

    async def get_db(path) -> TinyDB:
        return TinyDB(path)

    async def list_factions(self):
        raise NotImplementedError()

    async def get_faction(self, id: int):
        path = "{path}/{id}".format(path=self.faction_db_path, id=id)
        raise NotImplementedError()
