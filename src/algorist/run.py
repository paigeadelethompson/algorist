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

import asyncio
import os
from processor import inbox as processor_inbox
from sandbox import inbox as sandbox_inbox
from bot import Algorist, BotProcessor

async def _bot():
    b = Algorist()
    async with asyncio.TaskGroup() as tg:
        await asyncio.gather(
            bot.start(os.environ.get("DISCORD_TOKEN")),
            tg.create_task(BotProcessor(b)))

async def _insecure():
    async with asyncio.TaskGroup() as tg:
        if os.environ.get("DISCORD_TOKEN") is None:
            raise Exception("DISCORD_TOKEN environment variable not set")
        await asyncio.gather(
            tg.create_task(sandbox_inbox()),
            tg.create_task(processor_inbox()),
            tg.create_task(_bot()))

def insecure():
    asyncio.get_event_loop().run(_insecure())

def bot():
    asyncio.run(_bot())

def processor():
    asyncio.run(processor_inbox())

def sandbox():
    asyncio.run(sandbox_inbox())
