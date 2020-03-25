import asyncio
import websockets
import json
import pandas as pd
import numpy as np
import requests
import xlsxwriter
import time

# from websocket.export_libraries import *
# from websocket.variables import *

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
d_lookup.update({'_id': '_id', '_i': '_i', 'snapshot': '_s', 'E': 'E','err':'err','code':'code'})
inv_d_lookup = {v: k for k, v in d_lookup.items()}

fields = list(d_lookup.values())
HEARTBEAT_MESSAGE = json.dumps({"_id": 16})


async def myHeartbeat(websocket, heartbeat_message):
    while True:
        await asyncio.sleep(5)
        try:
            res = await websocket.send(heartbeat_message)
            print('heartbeat is sent')
        except Exception as e:
            print(f"myHeartbeat error is raised : {str(e)}")


data = []


async def mySubscribe(websocket):
    subscribe_msg = json.dumps({
        "_id": 1,
        "id": 1,
        "symbols": ["H1758"],
        "fields": fields
    })
    try:
        websocket.send(subscribe_msg)
        # r = await websocket.recv()
        # print('subscribe_msg is received')
        return json.loads(r)
        # print(data[-1])
        # data.append(json.loads(r))
        # return True
    except Exception as e:
        print(f"mySubscribe error is raised :{str(e)}")
        print(str(e))


async def myLogin(websocket):
    login_msg = json.dumps({
        "_id": 64,
        "user": "IP-AKNKE4623-91746",
        "password": "91746",
        "info": "1.5.22.4",
        "resource": "fxplus"})
    await websocket.send(login_msg)

    a = await websocket.recv()

    if json.loads(a)['result'] == 100:
        print('Login is successfull')
        await websocket.send(HEARTBEAT_MESSAGE)
        print(f'First heartbeat is sent at {time.time()}')
        return True


SUBSCRIBE_MESSAGE = json.dumps({
    "_id": 1,
    "id": 1,
    "symbols": ["H1758"],
    "fields": fields
})


async def main(uri='wss://websocket.foreks.com/websocket', subscribe_msg=SUBSCRIBE_MESSAGE):
    async with websockets.connect(uri) as ws:
        if await myLogin(websocket=ws):
            await ws.send(subscribe_msg)
            while True:
                # await myHeartbeat(ws)
                while True:
                    message_str = await asyncio.wait_for(ws.recv(), None)
                    message = json.loads(message_str)
                    data.append(message)
                    print(f"new data append and new length : {len(data)}")
                    if len(data)>3:
                        if data[-1] == data[-2]:
                            print('lutfen stop')

            # asyncio.ensure_future(mySubscribe(websocket=ws))
            # asyncio.ensure_future(myHeartbeat(websocket=ws))
            # await asyncio.gather(mySubscribe(ws),myHeartbeat(ws))
            # await mySubscribe(websocket=ws)
            # print('while true')
            # # await myHeartbeat(websocket=ws)
            # await myHeartbeat(websocket=ws)
            # print(len(data))


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    # print(len(data))
    loop.close()
    x = pd.DataFrame(data)
    x.columns = list(map(lambda col: inv_d_lookup[col], x.columns))
