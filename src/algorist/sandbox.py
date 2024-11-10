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

import os, statistics, math
from aiozmq.rpc import AttrHandler, serve_rpc, method
from RestrictedPython import compile_restricted, safe_builtins
import numpy, pandas, matplotlib, itertools
import user, faction

class SandBox(AttrHandler):
    def __init__(self):
        self.sandbox_globals = {
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
        self.sandbox_locals = {}
        super().__init__()

    @method
    async def execute(self, command: str):
        code = compile_restricted(
            command,
            filename='<inline code>',
            mode='eval')
        exec(code, self.sandbox_globals, self.sandbox_locals, None)

async def inbox():
    if os.environ.get("SANDBOX_PROCESSOR_BIND_HOST") is None:
        raise Exception("SANDBOX_PROCESSOR_BIND_HOST not set")
    bind_host = os.environ.get("SANDBOX_PROCESSOR_BIND_HOST")
    server = await serve_rpc(SandBox(), bind=bind_host)
    server_addr = list(server.transport.bindings()).pop(0)
    await server.wait_closed()