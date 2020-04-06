# from websocket.export_libraries import *
# from websocket.variables import *
'''
bilinmeyenler sorulacaklar: Price, TimeMs
'''
import asyncio
from asyncpg.pool import Pool
import websockets
import json
import pandas as pd
import time
from constants import *
import logging
from postgreSQL_db.config import *
import asyncpg
from asyncpg.pool import *

logger = logging.getLogger('websockets')
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())

akbnk_id = 'H1758'
btc_try_id = 'o850'
btc_usd_id = 'o1698'
thyao_id = 'H2796'
acsel_id = 'H2898'
tknosa_id = 'H1582'

aa = {
    'H1758': 'AKBNK',
    'o850': 'BTC_TRY',
    'o1698': 'BTC_USD',
    'H2796': 'THYAO',
    'H2898': 'ACSEL',
    'H1582': 'TKNSA'}

# fields_lookup = get_symbols.get_field_shortcodes(get_symbols.fields_subscribe)
field_df = pd.read_pickle(websocket_path / Path('outputs/fields_lookup.pickle'))
field_df_time = field_df.loc[field_df.type == 'TIME']
fields_lookup = field_df[['display', 'shortCode']].set_index('display').to_dict()['shortCode']
fields_lookup.update(
    {'_id': '_id', '_i': '_i', 'snapshot': '_s', 'E': 'E', 'err': 'err', 'code': 'code'
        , 'mydate': 'mydate', 'my_time': 'my_time'
     })

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
    btc_try_id,
    btc_usd_id,
    thyao_id, acsel_id, tknosa_id

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
        print('HEARTBEAT ..')
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

current_milli_time = lambda: int(round(time.time() * 1000))


def handle_message(msg):
    global MSG_COUNT
    if '_i' in msg.keys():
        # msg['my_date'] = pd.to_datetime(time.time(), unit='s')
        msg['my_time'] = current_milli_time()

        data[aa[msg['_i']]].append(msg)
        MSG_COUNT += 1
        if MSG_COUNT % 10 == 0:
            print(f'{MSG_COUNT}. mesaj alindi. :{msg}')

    else:
        print(f'not handled for message : {msg}')
        msg = None
    return msg


params = config()


async def create_pool(*, dsn: str, min_conn: int = 2, max_conn: int = 10, **kwargs):
    pool = await asyncpg.create_pool(dsn=dsn,
                                     min_size=min_conn,
                                     max_size=max_conn,
                                     **kwargs)
    logger.info("Pool created")
    return pool


def get_pool(dsn, loop):
    attempts = 20
    sleep_between_attempts = 3
    for _ in range(attempts):
        try:
            pool = loop.run_until_complete(create_pool(dsn=dsn))
        except Exception as e:
            logger.exception(e)
            time.sleep(sleep_between_attempts)
        else:
            return pool

    raise Exception(f"Could not connect to database using {dsn} after "
                    f"{attempts * sleep_between_attempts} seconds")


def get_query(msg, table):
    query = None
    if msg is not None:
        try:
            columns_ = ','.join(list(map(lambda k: inverse_fields_lookup[k], msg.keys())))
            values_ = tuple(msg.values())
            query = f"""INSERT INTO {table} ({columns_}) VALUES{values_};"""

        except Exception as e:
            print(e)
    return query


async def insert_ticker(message, pool, table: str) -> None:
    query = get_query(msg=message, table=table)
    async with pool.acquire() as connection:
        async with connection.transaction():
            await connection.execute(query)


async def get_message(*, websocket, insert_function):
    message_str = await websocket.recv()
    message = json.loads(message_str)
    message = handle_message(message)

    await insert_function(message)
    # if query is not None:
    #     try:
    #         conn = await asyncpg.connect(**params)
    #         await conn.execute(query)
    #     except Exception as e:
    #         print(str(e))


async def get_async(*, myLogin, handle_message):
    '''postgres://user:pass@host:port/database?option=value'''
    dsn = f'postgres://{params["user"]}:{params["password"]}@{params["host"]}:5432/{params["database"]}'
    uri = 'wss://websocket.foreks.com/websocket'
    subscribe_msg = MESSAGES['SUBSCRIBE_MESSAGE']
    async with websockets.connect(uri) as ws:
        if await myLogin(websocket=ws):
            await ws.send(subscribe_msg)
            program_starts = time.time()

            while True:
                insert_ticker_async = lambda response: insert_ticker(message=response, pool=Pool, table='time_series_5')
                pool = get_pool(dsn, asyncio.get_event_loop())
                await get_message(websocket=ws, insert_function=insert_ticker_async)
                loop = asyncio.get_event_loop()
                loop.run_until_complete(pool.close())
                # task_heartbeat = loop.create_task(myHeartbeat(ws, MESSAGES['HEARTBEAT_MESSAGE']))
                # task_get_message = loop.create_task(get_message(ws=ws))
                # await task_get_message
                # await task_heartbeat
                if time.time() - program_starts > 10:
                    program_starts = await myHeartbeat(ws, heartbeat_message=MESSAGES['HEARTBEAT_MESSAGE'])


def main():
    asyncio.get_event_loop().run_until_complete(
        get_async(myLogin=myLogin, handle_message=handle_message))
    # asyncio.get_event_loop().run_forever(
    #             get_async(myLogin=myLogin, handle_message=handle_message))


if __name__ == '__main__':
    main()

    df_data = [i for k, v in data.items() for i in v]
    df = pd.DataFrame(df_data)
    df.columns = list(map(lambda col: inverse_fields_lookup[col], df.columns))
    df['datetime'] = pd.to_datetime(df['DateTime'], unit='ms')
    df['mydatetime'] = pd.to_datetime(df['my_time'], unit='ms')
    df.to_pickle(websocket_path / Path('outputs') / Path('data_sample_5.pickle'))
