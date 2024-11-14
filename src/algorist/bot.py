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
import interactions
from aiozmq.rpc import connect_rpc
from interactions import listen, slash_command, slash_str_option


class Algorist(interactions.Client):
    @listen()
    async def on_ready(self):
        print(f'Logged on as {self.user}!')
        await self.change_presence(status=interactions.Status.ONLINE)

    @slash_command(name="e", description="Run sandboxed code", options=[slash_str_option(
        name="command", description="code to evaluate", required=True)])
    async def e(self, ctx: interactions.SlashContext, command: str):
        client = await connect_rpc(connect=os.environ.get("SANDBOX_PROCESSOR_BIND_HOST"))
        if ctx.guild != None and ctx.channel is not None:
            ret = await client.call.execute(ctx.guild.id, ctx.channel.id, command)
        else:
            ret = await client.call.execute(1, 1, command)
        client.close()
        await client.wait_closed()
        await ctx.send(str(ret))

    @slash_command(name="default_torn_api_key", description="Sets default API key", options=[slash_str_option(
        name="api_key", description="the default api key to use for Torn", required=True)])
    async def default_torn_api_key(self, ctx: interactions.SlashContext, api_key: str):
        client = await connect_rpc(connect=os.environ.get("SANDBOX_PROCESSOR_BIND_HOST"))
        ret = await client.call.set_default_torn_api_key(api_key)
        client.close()
        await client.wait_closed()
        await ctx.send(str(ret))

    @slash_command(name="link_torn_user", description="Links Discord user to Torn user", options=[slash_str_option(
        name="torn_user_id", description="the torn user id to link", required=True), slash_str_option(
        name="discord_user", description="the discord user id to link", required=True)])
    async def link_torn_user(self, ctx: interactions.SlashContext, torn_user_id: str, discord_user_id: str):
        client = await connect_rpc(connect=os.environ.get("SANDBOX_PROCESSOR_BIND_HOST"))
        ret = await client.call.link_torn_user(torn_user_id, discord_user_id)
        client.close()
        await client.wait_closed()
        await ctx.send(str(ret))

    @slash_command(name="set_torn_api_key", description="Sets API key", options=[slash_str_option(
        name="api_key", description="the api key to use for Torn", required=True)])
    async def set_default_torn_api_key(self, ctx: interactions.SlashContext, api_key: str):
        client = await connect_rpc(connect=os.environ.get("SANDBOX_PROCESSOR_BIND_HOST"))
        ret = await client.call.store_default_api_key(api_key, ctx.author.user.id)
        client.close()
        await client.wait_closed()
        await ctx.send(str(ret))


class BotProcessor(aiozmq.rpc.AttrHandler):
    def __init__(self, bot: Algorist):
        self.bot = bot
        super().__init__()

    @aiozmq.rpc.method
    def send_image_to_room(self, guild, channel, data):
        g = self.bot.get_guild(guild)
        c = g.get_channel(channel)
        raise NotImplementedError()

    @aiozmq.rpc.method
    def send_notification_to_room(self, guild, channel, data):
        g = self.bot.get_guild(guild)
        c = g.get_channel(channel)
        raise NotImplementedError()

    @aiozmq.rpc.method
    def send_private_message_to_user(self, user: str, data):
        raise NotImplementedError()


async def inbox(bot):
    if os.environ.get("BOT_PROCESSOR_BIND_HOST") is None:
        raise Exception("BOT_PROCESSOR_BIND_HOST not set")
    if os.environ.get("SANDBOX_PROCESSOR_BIND_HOST") is None:
        raise Exception('SANDBOX_PROCESSOR_BIND_HOST is not set')
    bind_host = os.environ.get("BOT_PROCESSOR_BIND_HOST")
    server = await aiozmq.rpc.serve_rpc(BotProcessor(bot), bind=bind_host)
    await server.wait_closed()
