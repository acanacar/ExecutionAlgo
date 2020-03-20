# from websocket import get_symbols
import asyncio
import websockets
import json

akbnk_id = 'H1758'
# d_lookup = get_symbols.get_field_shortcodes(get_symbols.fields_subscribe)

d_lookup = {'Ask': 'a',
            'High': 'h',
            'Close': 'cl',
            'Low': 'L',
            'Spread': 'sP',
            'VWAP': 'wa',
            'AskAmount0': 'w0',
            'Last': 'l',
            'BidPrice0': 'b0',
            'Direction': 'd',
            'Bid': 'b', 'AskPrice0': 'a0', 'Price': 'P',
            'BidAmount0': 'v0', 'Volume': 'v', 'Open': 'O'}
d_lookup.update({'_id': '_id', '_i': '_i', 'snapshot': '_s', 'E': 'E'})
inv_d_lookup = {v: k for k, v in d_lookup.items()}

fields = list(d_lookup.values())
data = []


async def login(uri):
    async with websockets.connect(uri) as websocket:
        login_msg = json.dumps({
            "_id": 64,
            "user": "IP-AKNKE4623-91746",
            "password": "91746",
            "info": "1.5.22.4",
            "resource": "fxplus"})
        try:
            await websocket.send(login_msg)
            a = await websocket.recv()

            if json.loads(a)['result'] == 100:
                await websocket.pong(json.dumps({"_id": 16}))
                print('login is completed.')
                return True
            else:
                return False

        except Exception as e:
            print(str(e))


async def subscribe_test(uri):
    async with websockets.connect(uri) as websocket:

        subscribe_msg = json.dumps({
            "_id": 1,
            "id": 1,
            "symbols": ["H1758"],
            "fields": fields
        })
        try:
            await websocket.send(subscribe_msg)
            r = await websocket.recv()
            print('subscribe_msg is received')
            data.append(json.loads(r))

        except Exception as e:
            print('hata burada')
            print(str(e))


async def subscribe(uri):
    async with websockets.connect(uri) as websocket:
        login_msg = json.dumps({
            "_id": 64,
            "user": "IP-AKNKE4623-91746",
            "password": "91746",
            "info": "1.5.22.4",
            "resource": "fxplus"})
        try:
            await websocket.send(login_msg)
            a = await websocket.recv()

            if json.loads(a)['result'] == 100:
                # await websocket.pong(json.dumps({"_id": 16}))
                subscribe_msg = json.dumps({
                    "_id": 1,
                    "id": 1,
                    "symbols": ["H1758"],
                    "fields": fields
                })
                await websocket.send(subscribe_msg)
                r = await websocket.recv()
                print('subscribe_msg is received')
                data.append(json.loads(r))

        except Exception as e:
            print(str(e))


loop = asyncio.get_event_loop()
loop.run_until_complete(subscribe('wss://websocket.foreks.com/websocket'))
# loop.run_until_complete(login('wss://websocket.foreks.com/websocket'))
# loop.run_until_complete(subscribe_test('wss://websocket.foreks.com/websocket'))

import pandas as pd

x = pd.DataFrame(data)
x.columns = list(map(lambda col: inv_d_lookup[col], x.columns))
