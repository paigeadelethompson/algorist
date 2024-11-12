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
from algorist.processor import inbox as processor_inbox
from algorist.sandbox import inbox as sandbox_inbox
from algorist.bot import Algorist
from algorist.bot import inbox as bot_inbox
import interactions as discord

client = Algorist(
    command_prefix=os.environ.get("DISCORD_BOT_PREFIX"),
    help_command=None,
    intents=discord.Intents.ALL)


async def _bot():
    if os.environ.get("DISCORD_BOT_PREFIX") is None:
        raise Exception("DISCORD_BOT_PREFIX is not set")
    if os.environ.get("DISCORD_TOKEN") is None:
        raise Exception("DISCORD_TOKEN environment variable not set")
    async with asyncio.TaskGroup() as tg:
        await asyncio.gather(
            client.astart(os.environ.get("DISCORD_TOKEN")),
            tg.create_task(bot_inbox(bot=client)))


async def _insecure():
    async with asyncio.TaskGroup() as tg:
        await asyncio.gather(
            tg.create_task(sandbox_inbox()),
            tg.create_task(processor_inbox()),
            tg.create_task(_bot()))


def insecure():
    asyncio.get_event_loop().run_until_complete(_insecure())


def bot():
    asyncio.get_event_loop().run_until_complete(_bot())


def processor():
    asyncio.get_event_loop().run_until_complete(processor_inbox())


def sandbox():
    asyncio.get_event_loop().run_until_complete(sandbox_inbox())
