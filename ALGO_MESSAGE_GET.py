# from dev.vars.variables import *
import asyncio
import logging


class FXPLUS_MESSENGER(asyncio.AbstractEventLoop):

    def __init__(self, ws, fx_plus_messages_queue):
        self.loop = asyncio.get_event_loop()
        self.fx_plus_messages_queue = fx_plus_messages_queue
        self.schedule_tasks()
        self.ws = ws

    @staticmethod
    def log_message(message):
        print(f"Message {message}")

    def schedule_tasks(self):
        self.loop.create_task(self.recv_data())

    async def recv_data(self):
        while True:
            try:
                message_str = await self.ws.recv()
                await self.fx_plus_messages_queue.put(message_str)
                self.log_message(message_str)
            except Exception as e:
                logging.exception(e)
