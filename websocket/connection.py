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

akbnk_id = 'H1758'
btc_try_id = 'o850'
btc_usd_id = 'o1698'
thyao_id = 'H2796'
aa = {
    'H1758': 'AKBNK',
    'o850': 'BTC_TRY',
    'o1698': 'BTC_USD',
}

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
    # akbnk_id,
    btc_try_id,
    btc_usd_id,
    # thyao_id

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
    while True:
        await asyncio.sleep(5)
        try:
            res = await websocket.send(heartbeat_message)
            print('heartbeat is sent')
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


async def main(uri='wss://websocket.foreks.com/websocket', subscribe_msg=MESSAGES['SUBSCRIBE_MESSAGE']):
    async with websockets.connect(uri) as ws:
        if await myLogin(websocket=ws):
            await ws.send(subscribe_msg)
            message_count = 0
            while True:
                # await myHeartbeat(ws)
                while True:
                    message_str = await asyncio.wait_for(ws.recv(), None)
                    message = json.loads(message_str)
                    message['my_date'] = time.time()
                    data[aa[message['_i']]].append(message)
                    message_count += 1
                    # print(f"new data append and new length : {len(data)}")
                    if message_count % 6 == 0:
                        print(message_count)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    # print(len(data))
    loop.close()
    x = pd.DataFrame(data)
    x.columns = list(map(lambda col: inverse_fields_lookup[col], x.columns))
    x['datetime'] = pd.to_datetime(x['DateTime'], unit='ms')
    x['mydatetime'] = pd.to_datetime(x['mydate'], unit='s')
