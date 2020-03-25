# Dieter Jordens
# https://medium.com/better-programming/how-to-create-a-websocket-in-python-b68d65dbd549
import asyncio
import websockets

async def produce(message: str, host: str, port: int) -> None:
    websocket_resource_url = f"ws://{host}:{port}"
    async with websockets.connect(websocket_resource_url) as ws:
        ws.send(message)
        await ws.recv()


loop = asyncio.get_event_loop()
loop.run_until_complete(produce(message='hi', host='localhost', port=4000))
loop.run_forever()