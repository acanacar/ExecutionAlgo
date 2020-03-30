# from websocket.export_libraries import *
# from websocket.variables import *
'''
bilinmeyenler sorulacaklar: Price, TimeMs
'''
import asyncio
import websockets
import json
import pandas as pd
import time
from constants import *

import logging

logger = logging.getLogger('websockets')
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())

akbnk_id = 'H1758'
btc_try_id = 'o850'
btc_usd_id = 'o1698'
thyao_id = 'H2796'
aa = {
    'H1758': 'AKBNK',
    'o850': 'BTC_TRY',
    'o1698': 'BTC_USD',
    'H2796': 'THYAO'}

# fields_lookup = get_symbols.get_field_shortcodes(get_symbols.fields_subscribe)
field_df = pd.read_pickle(websocket_path / Path('outputs/fields_lookup.pickle'))
field_df_time = field_df.loc[field_df.type == 'TIME']
fields_lookup = field_df[['display', 'shortCode']].set_index('display').to_dict()['shortCode']
fields_lookup.update(
    {'_id': '_id', '_i': '_i', 'snapshot': '_s', 'E': 'E', 'err': 'err', 'code': 'code', 'mydate': 'mydate'})

inverse_fields_lookup = {v: k for k, v in fields_lookup.items()}

fields = list(fields_lookup.values())

fields_ = [
    'DateTime',
    # 'Time', 'Date', 'TimeMs', 'BestBidTime', 'BestAskTime',
    'Last',
    # 'Ticker',
    'Bid',
    # 'BidPrice0', 'BidAmount0',
    'Ask',
    # 'AskPrice0', 'AskAmount0'
]

fields = [fields_lookup[f] for f in fields_]
symbols_to_subscribe = [
    akbnk_id,
    # btc_try_id,
    # btc_usd_id,
    thyao_id

]
MESSAGES = {
    'HEARTBEAT_MESSAGE': json.dumps({"_id": 16}),

    'LOGIN_MSG': json.dumps({
        "_id": 64,
        "user": "IP-AKNKE4623-91746",
        "password": "91746",
        "info": "1.5.22.4",
        "resource": "fxplus"})
    ,
    'SUBSCRIBE_MESSAGE': json.dumps({
        "_id": 1,
        "id": 1,
        "symbols": symbols_to_subscribe,
        "fields": fields
    })}
data = {aa[symbol]: [] for symbol in symbols_to_subscribe}


async def myHeartbeat(websocket, heartbeat_message):
    try:
        await websocket.send(heartbeat_message)
        print('heartbeat is sent')
        return time.time()
    except Exception as e:
        print(f"myHeartbeat error is raised : {str(e)}")


async def myLogin(websocket, login_msg=MESSAGES['LOGIN_MSG']):
    await websocket.send(login_msg)

    a = await websocket.recv()

    if json.loads(a)['result'] == 100:
        print('Login is successfull')
        await websocket.send(MESSAGES['HEARTBEAT_MESSAGE'])
        print(f'First heartbeat is sent at {time.time()}')
        return True


MSG_COUNT = 0


def create_fxplus_response(msg):
    global MSG_COUNT
    if '_i' in msg.keys():
        msg['my_date'] = pd.to_datetime(time.time(), unit='s')
        data[aa[msg['_i']]].append(msg)
        MSG_COUNT += 1
        if MSG_COUNT % 10 == 0:
            print(f'{MSG_COUNT}. mesaj alindi. :{msg}')

    else:
        print(f'not handled for message : {msg}')


async def data_print():
    print('burdayiz_1')
    await asyncio.sleep(10)
    print('burdayiz_2')
    # print(pd.DataFrame(data))


async def get_message(ws):
    message_str = await ws.recv()
    message = json.loads(message_str)
    create_fxplus_response(message)


async def get_async(*, myLogin, create_fxplus_response):
    uri = 'wss://websocket.foreks.com/websocket'
    subscribe_msg = MESSAGES['SUBSCRIBE_MESSAGE']
    message_count = 0
    async with websockets.connect(uri) as ws:
        if await myLogin(websocket=ws):
            await ws.send(subscribe_msg)
            program_starts = time.time()

            while True:
                await get_message(ws)
                # loop = asyncio.get_event_loop()
                # task_heartbeat = loop.create_task(myHeartbeat(ws, MESSAGES['HEARTBEAT_MESSAGE']))
                # task_data_print = loop.create_task(data_print())
                # task_get_message = loop.create_task(get_message(ws=ws))
                # await task_get_message
                # await task_data_print
                # await task_heartbeat
                if time.time() - program_starts > 10:
                    program_starts = await myHeartbeat(ws, heartbeat_message=MESSAGES['HEARTBEAT_MESSAGE'])


def main():
    asyncio.get_event_loop().run_until_complete(
        get_async(myLogin=myLogin, create_fxplus_response=create_fxplus_response))
    # asyncio.get_event_loop().run_forever(
    #             get_async(myLogin=myLogin, create_fxplus_response=create_fxplus_response))


if __name__ == '__main__':
    main()

    df_data = [i for k, v in data.items() for i in v]
    df = pd.DataFrame(df_data)
    df.columns = list(map(lambda col: inverse_fields_lookup[col], x.columns))
    df['datetime'] = pd.to_datetime(df['DateTime'], unit='ms')
    df['mydatetime'] = pd.to_datetime(df['my_date'], unit='s')
    df.to_pickle(websocket_path / Path('outputs') / Path('data_sample_2.pickle'))
