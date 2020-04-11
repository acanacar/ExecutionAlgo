from asyncpg.pool import *
from websocket.variables import *

logger = logging.getLogger('websockets')
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())

MSG_COUNT = 0


async def myLogin(websocket, login_msg=MESSAGES['LOGIN_MSG']):
    await websocket.send(login_msg)

    a = await websocket.recv()

    if json.loads(a)['result'] == 100:
        print('Login is successfull')
        return True


current_milli_time = lambda: int(round(time.time() * 1000))


def create_fxplux_response(msg):
    global MSG_COUNT
    if '_i' in msg.keys():
        msg['my_time'] = current_milli_time()

        msg['datetime_pd'] = str(pd.to_datetime(msg['my_time'], unit='ms', utc=True)
                                 .tz_convert('Europe/Istanbul'))
        MSG_COUNT += 1
        if MSG_COUNT % 10 == 0:
            print(f'{MSG_COUNT}. mesaj alindi. :{msg}')
    else:
        print(f'not handled for message : {msg}')
        msg = None
    return msg


async def get_async_fxplus(*, insert_function):
    uri = 'wss://websocket.foreks.com/websocket'

    async with websockets.connect(uri, ping_interval=14) as ws:
        if await myLogin(websocket=ws):
            await ws.send(MESSAGES['SUBSCRIBE_MESSAGE'])
            if ws.closed:
                print("connection is closed")
            while True:

                message_str = await ws.recv()
                message = json.loads(message_str)

                response = create_fxplux_response(message)

                if response is not None:
                    await insert_function(response)
                else:
                    print('response is None')


async def recv_data(ws, insert_function):
    while True:
        message_str = await ws.recv()
        message = json.loads(message_str)
        response = create_fxplux_response(message)

        if response is not None:
            try:
                await insert_function(response)
            except Exception as e:
                print('Insert Error')
        else:
            print('response is None')


len_o = 0


async def display_(conn_pool, query):
    #     query = f'''SELECT * FROM time_series_5
    #             WHERE _i='o850'
    #             AND my_time > {1585791135038}
    #             ORDER BY datetime DESC
    # --             LIMIT 2
    #             '''
    queries = [
        f'''
            SELECT 	*
            FROM 	timescale_executionalgo_t2
            WHERE 	1=1
            AND     _i = 'H2796'
            AND     last IS NOT NULL
            AND 	datetime_pd > NOW() - interval '1 MINUTES';'''
        ,
        f'''
            SELECT 	*
            FROM 	timescale_executionalgo_t2
            WHERE 	1=1
            AND     _i = 'H2796'
            AND     last IS NOT NULL
            AND 	datetime_pd > NOW() - interval '65 MINUTES';'''
    ]
    tasks = [
        conn_pool.fetch(queries[0]),
        conn_pool.fetch(queries[1])
    ]
    results = asyncio.gather(*tasks)

    while True:
        global len_o

        """        
        query = f'''SELECT 	* 
                    FROM 	timescale_executionalgo_t2
                    WHERE 	1=1
                    AND     _i = 'H2796'
                    AND     last IS NOT NULL 
                    AND 	datetime_pd > NOW() - interval '1 MINUTES';'''
        try:
            output = await conn_pool.fetch(query)
            if len(output) > 1:
                print(len(output))
                len_o = len(output)
        except Exception as e:
            print(str(e))
        """
        try:
            output = await results
            for x in output:
                if len(x) > 5:
                    print(len(x))
        except Exception as e:
            print(str(e))


a = 0
b = 0


async def display__(conn_pool,ind, query):
    global a, b
    while 1:
        try:
            output = await conn_pool.fetch(query)
            if len(output) > 5:
                print(len(output))
        except Exception as e:
            print(str(e))


QUERIES = [
    (1, f'''
            SELECT 	* 
            FROM 	timescale_executionalgo_t2
            WHERE 	1=1
            AND     _i = 'o850'
            AND     last IS NOT NULL
            AND 	datetime_pd > NOW() - interval '1 MINUTES';''')
    ,
    (2, f'''
            SELECT 	* 
            FROM 	timescale_executionalgo_t2
            WHERE 	1=1
            AND     _i = 'o850'
            AND     last IS NOT NULL 
            AND 	datetime_pd > NOW() - interval '10 MINUTES';''')
]


async def handle_fxplus(insert_function, pool):
    ws = await websockets.connect(uri='wss://websocket.foreks.com/websocket', ping_interval=14)
    if await myLogin(websocket=ws):
        await ws.send(MESSAGES['SUBSCRIBE_MESSAGE'])
        asyncio.ensure_future(recv_data(ws=ws, insert_function=insert_function))
        # asyncio.ensure_future(display_(conn_pool=pool))
        queries = QUERIES
        for i, query in queries:
            asyncio.ensure_future(display__(conn_pool=pool,ind=i, query=query))

# 1854157108
