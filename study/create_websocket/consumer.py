# Dieter Jordens

import asyncio
import logging
import websockets
from websockets import WebSocketClientProtocol

logging.basicConfig(level=logging.INFO)


async def consumer_handler(websocket: WebSocketClientProtocol) -> None:
    async for message in websocket:
        log_message(message)


async def consume(hostname: str, port: int) -> None:
    websocket_resource_url = f"ws://{hostname}:{port}"
    async with websockets.connect(websocket_resource_url) as websocket:
        await consumer_handler(websocket)


def log_message(message: str) -> None:
    logging.info(f"Message {message}")


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(consume("localhost", port=4000))
    loop.run_forever()
