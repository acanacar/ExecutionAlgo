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

akbnk_id = 'H1758'
btc_try_id = 'o850'
btc_usd_id = 'o1698'
thyao_id = 'H2796'

aa = {
    'H1758': 'akbnk',
    'o850': 'btc_try',
    'o1698': 'btc_usd',
}

# fields_lookup = get_symbols.get_field_shortcodes(get_symbols.fields_subscribe)
field_df = pd.read_pickle('/root/PycharmProjects/ExecutionAlgo/websocket/outputs/fields_lookup.pickle')
field_df_time = field_df.loc[field_df.type == 'TIME']
fields_lookup = field_df[['display', 'shortCode']].set_index('display').to_dict()['shortCode']
fields_lookup.update(
    {'_id': '_id', '_i': '_i', 'snapshot': '_s', 'E': 'E', 'err': 'err', 'code': 'code', 'mydate': 'mydate'})

inverse_fields_lookup = {v: k for k, v in fields_lookup.items()}

fields = list(fields_lookup.values())

# for i in range(10):
#     for item in ['b','a','v','w']:
#         print(f"'{item}{i}',")
fields = ['t', 'TT',
          'b0', 'v0', 'a0', 'w0', 'b1', 'v1', 'a1', 'w1', 'b2', 'v2', 'a2', 'w2',
          'b3', 'v3', 'a3', 'w3', 'b4', 'v4', 'a4', 'w4', 'b5', 'v5', 'a5', 'w5',
          'b6', 'v6', 'a6', 'w6', 'b7', 'v7', 'a7', 'w7', 'b8', 'v8', 'a8', 'w8',
          'b9', 'v9', 'a9', 'w9']
fields_ = [
            'DateTime',
           # 'Time', 'Date', 'TimeMs', 'BestBidTime', 'BestAskTime',
           # 'TradeNumber',
           'Last',
           # 'Ticker',
           'Bid',
           # 'BidPrice0', 'BidAmount0',
           'Ask',
           # 'AskPrice0', 'AskAmount0'
           ]
# fields_ = ['DateTime', 'Ticker', 'Price', 'Last',
#            'Bid', 'BidPrice0', 'BidAmount0',
#            'Ask', 'AskPrice0', 'AskAmount0'
#            ]
# fields_ = ['BidPrice1', 'BidAmount1', 'AskPrice1', 'AskAmount1', 'BidPrice2', 'BidAmount2', 'AskPrice2', 'AskAmount2',
#      'BidPrice3', 'BidAmount3', 'AskPrice3', 'AskAmount3', 'BidPrice4', 'BidAmount4', 'AskPrice4', 'AskAmount4',
#      'BidPrice5', 'BidAmount5', 'AskPrice5', 'AskAmount5', 'BidPrice6', 'BidAmount6', 'AskPrice6', 'AskAmount6',
#      'BidPrice7', 'BidAmount7', 'AskPrice7', 'AskAmount7', 'BidPrice8', 'BidAmount8', 'AskPrice8', 'AskAmount8',
#      'BidPrice9', 'BidAmount9', 'AskPrice9', 'AskAmount9']
# fields_ = fields_ + ['DateTime', 'Time', 'Date']
fields = [fields_lookup[f] for f in fields_]

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
        "symbols": [
            # akbnk_id, btc_try_id, btc_usd_id,
            thyao_id
        ],
        "fields": fields
    })}
data = []

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
            while True:
                # await myHeartbeat(ws)
                while True:
                    message_str = await asyncio.wait_for(ws.recv(), None)
                    message = json.loads(message_str)
                    # message['symbol'] = aa[message['_id']]
                    message['mydate'] = time.time()
                    data.append(message)
                    # print(f"new data append and new length : {len(data)}")
                    if len(data) % 12 == 0:
                        print(len(data))


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    # print(len(data))
    loop.close()
    x = pd.DataFrame(data)
    x.columns = list(map(lambda col: inverse_fields_lookup[col], x.columns))
    x['datetime'] = pd.to_datetime(x['DateTime'], unit='ms')
    x['mydatetime'] = pd.to_datetime(x['mydate'], unit='s')
