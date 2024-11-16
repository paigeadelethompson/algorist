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

import traceback
from aiozmq.rpc import AttrHandler, method
from RestrictedPython import compile_restricted
from algorist.sandbox.context import ExecutionContext
from algorist.sandbox import module_logger

class SandBoxService(AttrHandler):
    def __init__(self, content_processor_bind_host):
        module_logger.info("Creating SandBox service")
        self.content_processor_bind_host = content_processor_bind_host
        self.ctx = {}
        super().__init__()

    async def get_context(self, guild, channel) -> ExecutionContext:
        hash_id = await ExecutionContext.hash_id(guild, channel)
        if self.ctx.get(hash_id) is None:
            module_logger.info("New sandbox execution context requested: {} {} {}".format(
                guild,
                channel,
                hash_id))
            self.ctx[hash_id] = ExecutionContext(
                guild,
                channel,
                self.content_processor_bind_host)
        return self.ctx.get(hash_id)

    @method
    async def execute(self, guild: str, channel: str, command: str):
        ctx = await self.get_context(guild, channel)
        locals = ctx.persisted_locals
        try:
            code = compile_restricted(
                "{command}".format(
                    command=command),
                filename='<inline code>',
                mode='exec')
            exec(code, ctx.globals, locals)
            ctx.persisted_locals.update(
                dict([(index, locals.get(index))
                      for index in locals.keys()
                      if index.upper() == index]))
        except Exception as e:
            traceback.print_exception(e)
        finally:
            return dict(
                [(index, locals.get(index))
                 for index in locals.keys()
                 if not index.upper() == index])


