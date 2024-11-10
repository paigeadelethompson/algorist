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

import discord
from discord.ext import commands
from aiozmq.rpc import connect_rpc

class Algorist(discord.Client):
    def __init__(self):
        super().__init__()
    async def on_ready(self):
        print(f'Logged in as {self.user}')

    @commands.command()
    async def e(self, ctx):
        if os.environ.get("SANDBOX_PROCESSOR_BIND_HOST") is None:
            raise Exception('SANDBOX_PROCESSOR_BIND_HOST is not set')
        try:
            client = await connect_rpc(connect=os.environ.get("SANDBOX_PROCESSOR_BIND_HOST"))
            ret = await client.call.execute(ctx.message.content)
            client.close()
            await client.wait_closed()
        except:
            pass