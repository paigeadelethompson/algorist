import requests
import json
import sys, os
from tinydb import TinyDB, Query
import asyncio
from aiohttp import web
import aioprocessing

class AlgoristDB:
    def __init__(self):
        if os.environ.get("FACTION_DB_PATH") == None:
            raise Exception("FACTION_DB_PATH not set")
        if os.environ.get("USER_DB_PATH") == None:
            raise Exception("USER_DB_PATH not set")
        if os.environ.get("CONFIG_DB_PATH") == None:
            raise Exception("CONFIG_DB_PATH not set")
        
        self.faction_db_path = os.environ.get("FACTION_DB_PATH")
        self.user_db_path = os.environ.get("USER_DB_PATH")
        self.config_db_path = os.environ.get("CONFIG_DB_PATH")

        if not os.path.isdir(self.faction_db_path):
            raise Exception("FACTION_DB_PATH should be a directory")
        if not os.path.isdir(self.user_db_path):
            raise Exception("USER_DB_PATH should be a directory")
        if not os.path.isfile(self.config_db_path):
            raise Exception("FACTION_DB_PATH should be a file name")

        if not os.access(self.faction_db_path, os.W_OK):
            raise Exception("FACTION_DB_PATH isn't writable")
        if os.access(self.user_db_path, os.W_OK):
            raise Exception("USER_DB_PATH isn't writable")
        if os.access(self.config_db_path, os.W_OK):
            raise Exception("CONFIG_DB_PATH isn't writable")

    async def _get_db(self, path):
        if not os.path.exists(path):
            raise Exception("user id does not exist")
        return TinyDB(path)

    async def list_users(self):
        raise NotImplementedError()

    async def list_factions(self):
        raise NotImplementedError()

    async def get_user(self, id: int):
        path = "{path}/{id}".format(path=self.user_db_path, id=id)
        return self._get_db(path)

    async def get_faction(self, id: int):
        path = "{path}/{id}".format(path=self.faction_db_path, id=id)
        return self._get_db(path)

    async def get_config(self):
        return self._get_db(self.config_db_path)

    async def save_user(self, user: User):
        raise NotImplementedError()

    async def save_user_hof(self, user_hof: UserHOF):
        raise NotImplementedError()

class TornV2API:
    def __init__(self, api_key=None):
        self._base_url = "https://api.torn.com/v2"
        if api_key == None: 
            conf = AlgoristDB().get_config()
            result = [index for index in conf.all() if index.key == "api_key"]
            if len(result) <= 0:
                raise Exception("main api_key not set")
            elif len(result > 1):
                raise NotImplementedError()
            self.api_key = result.pop().value
        else:
            self.api_key = api_key

    '''
    Documentation:
    https://www.torn.com/swagger/index.html#/User/get_user
    '''
    async def get_user(self, id):
        query = "{base}/user?key={api_key}&id={id}&striptags=true".format(
            base=self._base_url, api_key=self.api_key, id=id)
        async with aiohttp.request('GET', query) as resp:
            assert resp.status == 200
            return resp

class Faction:
    def __init__(self, payload, api_key=None):
        self.payload = json.loads(payload)

class UserHOF:
    '''
    When requesting selection with Limited,
    Full or Custom key, battle_stats selection will be populated.
    '''
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

class User:
    def __init__(payload):
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
