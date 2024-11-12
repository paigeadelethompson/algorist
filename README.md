# Intro
A Torn V2 API based Discord bot built on service-oriented architecture.
The bot is divided into logical sections that utilize `aiozmq` and it's 
RPC functionality for communication. The bot features a Python expression
evaluator sandbox for performing analytical operations on collected Torn
data for user and faction stats. The sandbox provides:
- Pandas
- matplotlib 
- numpy
- base python math modules (statistics, math)

The evaluator can be leveraged by a user with the appropriate 
permissions using the Discord slash command: `/e` for example:
```
/e [(index.name(), index.cur_hp()) for index in FactionDB().my().users()]
```

The bot also provides the following slash commands:
- `/set_default_torn_api_key <api_key>`
- `/link_torn_user <torn_user_id> <discord_user>`
- `/set_torn_api_key <api_key>`

The difference between `set_default_torn_api_key` and `set_torn_api_key`
being that the latter provides a means for Discord users who are linked
to a Torn ID to provide an API key and thus providing more insight into 
their account than can be obtained by the former.

## Design
The bot is compartmentalized into 3 separate services: 
- The discord client
- Request processor (Torn API requests, encryption/decryption operations)
- The Sandbox (Python executive, local database storage & retrieval)

In the process of setting API keys, the bot service sends the API key to 
the sandbox service for storage. When storing the key, the sandbox service
first sends the key to the request processor service to be encrypted, and 
that encrypted value is returned to the sandbox service for storage.

The request processor itself doesn't expose a means for de-encryption to other services,
but rather instead performs de-encryption of the API key for itself of 
whichever API key is sent then performs an API request to the Torn V2 API. The takeaway here
is that the risks associated with creating Python executive sandboxes are further mitigated,
but in general is a good practice for sensitive data-at-rest.

### Sandbox security 
The sandbox is constructed by first byte compiling the request and passing it to `exec` in conjunction
with `RestrictedPython`. For more information regarding this, refer to the `compile_restricted` and
`safe_builtins` sections of the documentation at https://restrictedpython.readthedocs.io/en/latest/idea.html

### Process hosting
The services can all operate as a single process or individual process, and each process further be
isolated on different physical hosts or as containers or chroot jails.

## Installation 
The preferred way is primarily using Docker:

- edit the `.env` file in the project:

```
USER_DB_PATH=/srv/algorist/db/user
FACTION_DB_PATH=/srv/algorist/db/faction
CONFIG_DB_PATH=/srv/algorist/db/config
SANDBOX_PROCESSOR_BIND_HOST=tcp://0.0.0.0:19818
REQUEST_PROCESSOR_BIND_HOST=tcp://0.0.0.0:19819
BOT_PROCESSOR_BIND_HOST=tcp://0.0.0.0:1982
DISCORD_TOKEN=xxxxxxxx
```
and replace the value of `DISCORD_TOKEN` with a valid token, refer to https://discord.com/developers/applications/
to create a Discord app and retrieve your token. 
- run `docker-compose up -d` This method will start 3 separate containers (one for each service.)
- Invite the bot to your channel using the invite link provided in the bot administration
portal: https://discord.com/developers/applications/1305197668036771912/installation

## Development 
Each of the three processes can be started on the same machine, start by entering the Python
virtualenv:
- `mkdir -p /tmp/algorist/db/{user,faction,config}`
- `mkdir -p /tmp/algorist/db/config/{sandbox,processor}`
- `chmod -R 777 /tmp/algorist`
- `poetry shell`
- `poetry install`

Note: `/tmp` directories will not persist between reboots.
- start the discord client
```
DISCORD_TOKEN="xxxxxxxxx"                           \
SANDBOX_PROCESSOR_BIND_HOST="tcp://127.0.0.1:19819" \
BOT_PROCESSOR_BIND_HOST="tcp://127.0.0.1:19818"     \
algorist-bot
```
- in another terminal run `poetry shell` from the project directory
and start the sandbox:
```
USER_DB_PATH=/srv/algorist/db/user                  \
FACTION_DB_PATH=/srv/algorist/db/faction            \
CONFIG_DB_PATH=/srv/algorist/db/config/sandbox      \
REQUEST_PROCESSOR_BIND_HOST="tcp://127.0.0.1:19820" \
SANDBOX_PROCESSOR_BIND_HOST="tcp://127.0.0.1:19819" \
algorist-sandbox
```
- open a third terminal, run `poetry shell`, and start the request
processor:
```
CONFIG_DB_PATH=/srv/algorist/db/config/processor    \
REQUEST_PROCESSOR_BIND_HOST="tcp://127.0.0.1:19820" \
algorist-processor
```

### Known problems
- `aiozmq` evidently doesn't support TLS as of yet: https://github.com/aio-libs/aiozmq/issues/123
. I can't ascertain whether the standard zeromq module for Python even supports this but will investigate further as needed.

### TODO
- support sending matplotlib graph from sandbox to Discord channel as an image

### Hardening ideas 
- possibly using the `ast` module to parse / determine the nature of the request
payload (input sanitization) before sending it into `exec`
- byte compiling code bundled with containers; prevents exposure of the source
- homomorphic encryption for data at rest: https://pypi.org/project/concrete-python/

### Torn V2 API Documentation
Documentation:
https://www.torn.com/swagger/index.html#/User/get_user
