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
from aiozmq.rpc import AttrHandler, serve_rpc, method
from RestrictedPython import compile_restricted, safe_builtins
from RestrictedPython.Eval import default_guarded_getiter
import numpy, pandas, matplotlib, itertools
import traceback
from io import BytesIO
from algorist import user, faction
from algorist.sandbox.config import SandBoxConfigDB

class ExecutionContext:
    async def hash_id(guild, channel):
        return hashlib.sha256(
            bytes(str(guild), 'utf-8') + bytes(str(channel), 'utf-8')).hexdigest()

    def __init__(self, guild, channel):
        self.guild = guild
        self.channel = channel
        self.globals = {
            '__builtins__': safe_builtins,
            '_getiter_': default_guarded_getiter,
            'NP': numpy,
            'P': pandas,
            'MPL': matplotlib,
            'IT': itertools,
            'U': user,
            'F': faction,
            'S': statistics,
            'M': math
        }
        self.locals = {"out": BytesIO()}

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
        try:
            ctx = await self.get_context(guild, channel)
            ctx.locals.get("out").truncate(0)
            code = compile_restricted(
                "{command}".format(
                    command=command),
                filename='<inline code>',
                mode='eval')
            exec(code, ctx.globals, ctx.locals)
            return ctx.locals.get("out").read().decode('utf-8')
        except Exception as e:
            traceback.print_exception(e)

    @method
    async def set_default_torn_api_key(self, api_key):
        try:
            SandBoxConfigDB().store_default_api_key(api_key)
        except Exception as e:
            traceback.print_exception(e)

    @method
    async def link_torn_user(self, torn_user_id, discord_user_id):
        try:
            raise NotImplementedError()
        except Exception as e:
            traceback.print_exception(e)

    @method
    async def set_torn_api_key(self, api_key, discord_user_id):
        try:
            raise NotImplementedError()
        except Exception as e:
            traceback.print_exception(e)

async def inbox():
    if os.environ.get("REQUEST_PROCESSOR_BIND_HOST") is None:
        raise Exception("REQUEST_PROCESSOR_BIND_HOST not set")
    if os.environ.get("SANDBOX_PROCESSOR_BIND_HOST") is None:
        raise Exception("SANDBOX_PROCESSOR_BIND_HOST not set")
    bind_host = os.environ.get("SANDBOX_PROCESSOR_BIND_HOST")
    server = await serve_rpc(SandBox(), bind=bind_host)
    await server.wait_closed()
