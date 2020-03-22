import asyncio
import websockets
import json

async def hello(uri):
    async with websockets.connect(uri) as websocket:
        msg = json.dumps({
            "_id": 64,
            "user": "IP-AKNKE4623-91746",
            "password": "91746",
            "info": "1.5.22.4",
            "resource": "fxplus"})
        try:
            await websocket.send(msg)
            a = await websocket.recv()
            if json.loads(a)['result'] == 100:
                print('result is succeeded')
                await websocket.pong(json.dumps({"_id": 16}))
                # data_msg = json.dumps({
                #     "_id": 64,
                #     "user": "IP-AKNKE4623-91746",
                #     "password": "91746",
                #     "info": "1.5.22.4",
                #     "resource": "fxplus"})
                # await websocket.send(data_msg)

                # heartbeat
            else:
                print('result is not succeeded')
        except Exception as e:
            print(str(e))


asyncio.get_event_loop().run_until_complete(
    # hello('ws://localhost:8765'))
    hello('wss://websocket.foreks.com/websocket'))
asyncio.get_event_loop().run_forever()