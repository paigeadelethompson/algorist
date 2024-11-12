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
import os, statistics, math
from aiozmq.rpc import AttrHandler, serve_rpc, method, connect_rpc
from RestrictedPython import compile_restricted, safe_builtins
import numpy, pandas, matplotlib, itertools
from tinydb import TinyDB

from algorist import user, faction

class SandBoxConfigDB:
    def __init__(self):
        if os.environ.get("CONFIG_DB_PATH") is None:
            raise Exception("CONFIG_DB_PATH not set")
        self.config_db_path = os.environ.get("CONFIG_DB_PATH")
        if not os.access(self.config_db_path, os.W_OK):
            raise Exception("CONFIG_DB_PATH isn't writable")
        self.db = TinyDB("{}/config.db".format(self.config_db_path))

    async def store_default_api_key(self, api_key):
        client = await connect_rpc(connect=os.environ.get("REQUEST_PROCESSOR_BIND_HOST"))
        encrypted_api_key = await client.call.encrypt_api_key(api_key)

        if len(self.db.table("default_api_key").all()) > 0:
            self.db.table("default_api_key").remove()

        self.db.table("default_api_key").insert({"value": encrypted_api_key})

    async def get_default_api_key(self):
        self.db.table("default_api_key").all().pop().get("value")

class ExecutionContext:
    async def hash_id(guild, channel):
        return hashlib.sha256(
            bytes(str(guild), 'utf-8') + bytes(str(channel), 'utf-8')).hexdigest()

    def __init__(self, guild, channel):
        self.guild = guild
        self.channel = channel
        self.globals = {
            '__builtins__': safe_builtins,
            'NP': numpy,
            'P': pandas,
            'MPL': matplotlib,
            'IT': itertools,
            'U': user,
            'F': faction,
            'S': statistics,
            'M': math,
        }
        self.locals = {"out": []}


class SandBox(AttrHandler):
    def __init__(self):
        self.ctx = {}
        super().__init__()

    async def get_context(self, guild, channel):
        hash_id = await ExecutionContext.hash_id(guild, channel)
        if self.ctx.get(hash_id) is None:
            self.ctx[hash_id] = ExecutionContext(guild, channel)
        return self.ctx.get(hash_id)

    @method
    async def execute(self, guild: str, channel: str, command: str):
        ctx = await self.get_context(guild, channel)
        code = compile_restricted(
            "{command}".format(
                command=command),
            filename='<inline code>',
            mode='eval')
        exec(code, ctx.globals, ctx.locals)
        return ctx.locals.get("out")

    @method
    async def set_default_torn_api_key(self, api_key):
        await SandBoxConfigDB().store_default_api_key(api_key)

    @method
    async def link_torn_user(self, torn_user_id, discord_user_id):
        raise NotImplementedError()

    @method
    async def set_torn_api_key(self, api_key, discord_user_id):
        raise NotImplementedError()


async def inbox():
    if os.environ.get("SANDBOX_PROCESSOR_BIND_HOST") is None:
        raise Exception("SANDBOX_PROCESSOR_BIND_HOST not set")
    bind_host = os.environ.get("SANDBOX_PROCESSOR_BIND_HOST")
    server = await serve_rpc(SandBox(), bind=bind_host)
    await server.wait_closed()
