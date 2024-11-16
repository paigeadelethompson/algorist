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
import threading
from algorist import module_logger, main_logger
from algorist.bot.service import Algorist
from algorist.processor.inbox import inbox as processor_inbox
from algorist.bot.inbox import inbox as bot_inbox
from algorist.sandbox.inbox import inbox as sandbox_inbox
from algorist.content.inbox import inbox as content_inbox

async def _insecure():
    if os.environ.get("DISCORD_TOKEN") is None:
        raise Exception("DISCORD_TOKEN environment variable not set")
    discord_token = os.environ.get("DISCORD_TOKEN")
    if os.environ.get("BOT_PROCESSOR_BIND_HOST") is None:
        bot_processor_bind_host = "tcp://127.0.0.1:19818"
    else:
        bot_processor_bind_host = os.environ.get("BOT_PROCESSOR_BIND_HOST")
    if os.environ.get("SANDBOX_PROCESSOR_BIND_HOST") is None:
        sandbox_processor_bind_host = "tcp://127.0.0.1:19819"
    else:
        sandbox_processor_bind_host = os.environ.get("SANDBOX_PROCESSOR_BIND_HOST")
    if os.environ.get("REQUEST_PROCESSOR_BIND_HOST") is None:
        request_processor_bind_host = "tcp://127.0.0.1:19820"
    else:
        request_processor_bind_host = os.environ.get("REQUEST_PROCESSOR_BIND_HOST")
    if os.environ.get("CONTENT_PROCESSOR_BIND_HOST") is None:
        content_processor_bind_host = "tcp://127.0.0.1:19821"
    else:
        content_processor_bind_host = os.environ.get("CONTENT_PROCESSOR_BIND_HOST")
    if os.environ.get("REQUEST_PROCESSOR_CONFIG_DB_PATH") is None:
        request_processor_config_db_path = "/tmp/algorist/config/request_processor"
    else:
        request_processor_config_db_path = os.environ.get("REQUEST_PROCESSOR_CONFIG_DB_PATH")
    if not os.access(request_processor_config_db_path, os.W_OK):
        raise Exception("CONFIG_DB_PATH isn't writable: {}".format(request_processor_config_db_path))
    if os.environ.get("CONTENT_PROCESSOR_CONFIG_DB_PATH") is None:
        content_processor_config_db_path = "/tmp/algorist/config/content_processor"
    else:
        content_processor_config_db_path = os.environ.get("CONTENT_PROCESSOR_CONFIG_DB_PATH")
    if not os.access(content_processor_config_db_path, os.W_OK):
            raise Exception("CONTENT_PROCESSOR_CONFIG_DB_PATH isn't writable: {}".format(
                content_processor_config_db_path))
    if os.environ.get("USER_DB_PATH") is None:
            user_db_path = "/tmp/algorist/db/user"
    else:
        user_db_path = os.environ.get("USER_DB_PATH")
    if not os.path.isdir(user_db_path):
        raise Exception("USER_DB_PATH should be a directory")
    if not os.access(user_db_path, os.W_OK):
        raise Exception("USER_DB_PATH isn't writable")
    client = Algorist(sandbox_processor_bind_host, content_processor_bind_host)
    module_logger.info("XXX starting synchronous threads, this sucks, refer to README known issues")
    t1 = threading.Thread(target=processor_inbox, args=(
        request_processor_bind_host,
        request_processor_config_db_path))
    t2 = threading.Thread(target=content_inbox, args=(
        content_processor_bind_host,
        request_processor_bind_host,
        content_processor_config_db_path,
        user_db_path))
    t1.start()
    t2.start()
    module_logger.info("starting task group in insecure mode")
    async with asyncio.TaskGroup() as tg:
        tg.create_task(client.astart(discord_token))
        tg.create_task(sandbox_inbox(sandbox_processor_bind_host, content_processor_bind_host))
        tg.create_task(bot_inbox(client, bot_processor_bind_host))

def insecure():
    asyncio.get_event_loop().run_until_complete(_insecure())

def bot():
    if os.environ.get("DISCORD_TOKEN") is None:
        raise Exception("DISCORD_TOKEN environment variable not set")
    if os.environ.get("BOT_PROCESSOR_BIND_HOST") is None:
        bot_processor_bind_host = "tcp://127.0.0.1:19818"
    else:
        bot_processor_bind_host = os.environ.get("BOT_PROCESSOR_BIND_HOST")
    if os.environ.get("SANDBOX_PROCESSOR_BIND_HOST") is None:
        sandbox_processor_bind_host = "tcp://127.0.0.1:19819"
    else:
        sandbox_processor_bind_host = os.environ.get("SANDBOX_PROCESSOR_BIND_HOST")
    if os.environ.get("CONTENT_PROCESSOR_BIND_HOST") is None:
        content_processor_bind_host = "tcp://127.0.0.1:19821"
    else:
        content_processor_bind_host = os.environ.get("CONTENT_PROCESSOR_BIND_HOST")
    discord_token = os.environ.get("DISCORD_TOKEN")
    client = Algorist(sandbox_processor_bind_host, content_processor_bind_host)
    asyncio.get_event_loop().run_until_complete(bot_inbox(
                client,
                bot_processor_bind_host))

def processor():
    if os.environ.get("REQUEST_PROCESSOR_BIND_HOST") is None:
        request_processor_bind_host = "tcp://127.0.0.1:19822"
    else:
        request_processor_bind_host = os.environ.get("REQUEST_PROCESSOR_BIND_HOST")
    if os.environ.get("REQUEST_PROCESSOR_CONFIG_DB_PATH") is None:
        request_processor_config_db_path = "/tmp/algorist/config/request_processor/"
    else:
        request_processor_config_db_path = os.environ.get("REQUEST_PROCESSOR_CONFIG_DB_PATH")
    t1 = threading.Thread(target=processor_inbox, args=(
        request_processor_bind_host,
        request_processor_config_db_path))
    t1.start()
    t1.join()

def sandbox():
    if os.environ.get("SANDBOX_PROCESSOR_BIND_HOST") is None:
        sandbox_processor_bind_host = "tcp://127.0.0.1:19819"
    else:
        sandbox_processor_bind_host = os.environ.get("SANDBOX_PROCESSOR_BIND_HOST")
    if os.environ.get("CONTENT_PROCESSOR_BIND_HOST") is None:
        content_processor_bind_host = "tcp://127.0.0.1:19821"
    else:
        content_processor_bind_host = os.environ.get("CONTENT_PROCESSOR_BIND_HOST")
    asyncio.get_event_loop().run_until_complete(sandbox_inbox(
                sandbox_processor_bind_host,
                content_processor_bind_host))

def content():
    if os.environ.get("CONTENT_PROCESSOR_BIND_HOST") is None:
        content_processor_bind_host = "tcp://127.0.0.1:19821"
    else:
        content_processor_bind_host = os.environ.get("CONTENT_PROCESSOR_BIND_HOST")
    if os.environ.get("REQUEST_PROCESSOR_BIND_HOST") is None:
        request_processor_bind_host = "tcp://127.0.0.1:19822"
    else:
        request_processor_bind_host = os.environ.get("REQUEST_PROCESSOR_BIND_HOST")
    if os.environ.get("CONTENT_PROCESSOR_CONFIG_DB_PATH") is None:
        content_processor_config_db_path = "/tmp/algorist/config/content_processor/"
    else:
        content_processor_config_db_path = os.environ.get("CONTENT_PROCESSOR_CONFIG_DB_PATH")
    if not os.access(content_processor_config_db_path, os.W_OK):
        raise Exception("CONTENT_PROCESSOR_CONFIG_DB_PATH isn't writable: {}".format(
            content_processor_config_db_path))
    if os.environ.get("USER_DB_PATH") is None:
        user_db_path = "/tmp/algorist/db/user/"
    else:
        user_db_path = os.environ.get("USER_DB_PATH")
    if not os.path.isdir(user_db_path):
        raise Exception("USER_DB_PATH should be a directory")
    if not os.access(user_db_path, os.W_OK):
        raise Exception("USER_DB_PATH isn't writable")
    t2 = threading.Thread(target=content_inbox, args=(
        content_processor_bind_host,
        request_processor_bind_host,
        content_processor_config_db_path,
        user_db_path))
    t2.start()
    t2.join()