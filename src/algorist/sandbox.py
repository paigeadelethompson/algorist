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
import numpy, pandas, matplotlib, itertools
from algorist import user, faction

_out = []
def display(data, depth=0, max_depth=2, max_extents=3):
    if depth == 0:
        _out.clear()
    elif depth > 1:
        _out.append()
    if type(data) == list:
        _out.append("list")
        if len(data) > max_extents:
            _ = [display(index) for index in data[:max_extents]]
            if len(data) > max_extents:
                _out.append("& {data} more".format(data=len(data)-max_extents))
        else:
            _out.append("empty")
    elif type(data) == bytes:
        _out.append("bytes")
        if len(data.keys()) > 0:
            _ = [display(index) for index in data[:max_extents]]
            if len(data) > max_extents:
                _out.append("& {data} more".format(data=len(data)-max_extents))
        else:
            _out.append("empty")
    elif type(data) == dict:
        _out.append("dict")
        if len(data.keys()) > 0:
            _ = [display(data.get(index)) for index in list(data.keys())[:max_extents]]
            if len(data.keys()) > max_extents:
                _out.append("..{data} more".format(data=len(data)-max_extents))
        else:
            _out.append("empty")
    elif type(data) == tuple:
        _out.append("tuple")
        _ = [display(index) for index in data[:max_extents]]
    else:
        if data is None:
            _out.append("empty")
        else:
            _out.append(str(data))


class ExecutionContext:
    async def hash_id(guild, channel):
        return hashlib.sha256(
            bytes(guild, 'utf-8') + bytes(channel, 'utf-8')).hexdigest()

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
            '_DISPLAY': display,
        }
        self.locals = {"__out": []}

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
            "_DISPLAY(({command}))".format(
                command=command),
            filename='<inline code>',
            mode='eval')
        exec(code, ctx.globals, ctx.locals, None)
        return ctx.get("_out")

async def inbox():
    if os.environ.get("SANDBOX_PROCESSOR_BIND_HOST") is None:
        raise Exception("SANDBOX_PROCESSOR_BIND_HOST not set")
    bind_host = os.environ.get("SANDBOX_PROCESSOR_BIND_HOST")
    server = await serve_rpc(SandBox(), bind=bind_host)
    await server.wait_closed()