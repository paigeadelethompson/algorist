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

import os
import aiozmq

class ResultProcessor(aiozmq.rpc.AttrHandler):
    def __init__(self):
        pass

    @aiozmq.rpc.method
    async def user_api_response(self, result):
        raise NotImplementedError()

    @aiozmq.rpc.method
    def encryption_result(self, result):
        raise NotImplementedError()

async def inbox():
    if os.environ.get("RESPONSE_PROCESSOR_BIND_HOST") is None:
        raise Exception("RESPONSE_PROCESSOR_BIND_HOST not set")
    bind_host = os.environ.get("RESPONSE_PROCESSOR_BIND_HOST")
    server = await aiozmq.rpc.serve_rpc(ResultProcessor(), bind=bind_host)
    server_addr = list(server.transport.bindings()).pop(0)
    await server.wait_closed()