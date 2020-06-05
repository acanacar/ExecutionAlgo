import asyncio
import json
import logging
import time

import websockets


async def heartbeat(websocket,MESSAGES):
    while True:
        try:
            await websocket.send(MESSAGES['HEARTBEAT_MESSAGE'])
            print(f'Heartbeat {time.ctime()}')
            logging.debug(f'Heartbeat {time.ctime()}')
        except Exception as e:
            logging.critical(e)

        await asyncio.sleep(11)


async def login(websocket,MESSAGES):
    await websocket.send(MESSAGES['LOGIN_MSG'])
    try:
        res_ = await websocket.recv()
        if json.loads(res_)['result'] == 100:
            print('Login is successfull')
            return True
        else:
            print('different login response')
            return False
    except Exception as e:
        print('Error in login', print(str(e)))


async def conn(MESSAGES):
    uri = 'wss://websocket.foreks.com/websocket'
    websocket = await websockets.connect(uri=uri, ping_interval=13)
    if await login(websocket,MESSAGES):
        return websocket

