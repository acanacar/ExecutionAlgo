from asyncpg.pool import *
from websocket.variables import *

logger = logging.getLogger('websockets')
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())

fields_ = [
    'DateTime',
    'Last',
    'Bid',
    'Ask',
]

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
        "symbols": symbols_to_subscribe,
        "fields": fields
    })}

last_heartbeat = time.time()


async def myHeartbeat(websocket, heartbeat_message):
    global last_heartbeat
    try:
        print(f'HEARTBEAT .. {time.time() - last_heartbeat}')
        last_heartbeat = time.time()
        await websocket.send(heartbeat_message)
    except Exception as e:
        print(f"myHeartbeat error is raised : {str(e)}")


async def myLogin(websocket, login_msg=MESSAGES['LOGIN_MSG']):
    await websocket.send(login_msg)

    a = await websocket.recv()

    if json.loads(a)['result'] == 100:
        print('Login is successfull')
        await myHeartbeat(websocket, MESSAGES['HEARTBEAT_MESSAGE'])
        print(f'First heartbeat is sent at {time.time()}')
        return True


current_milli_time = lambda: int(round(time.time() * 1000))

MSG_COUNT = 0


def create_fxplux_response(msg):
    global MSG_COUNT
    if '_i' in msg.keys():
        # msg['my_date'] = pd.to_datetime(time.time(), unit='s')
        msg['my_time'] = current_milli_time()
        MSG_COUNT += 1
        if MSG_COUNT % 10 == 0:
            print(f'{MSG_COUNT}. mesaj alindi. :{msg}')
    else:
        print(f'not handled for message : {msg}')
        msg = None
    return msg


prog_st = time.time()


async def send_heartbeat():
    while True:
        # global prog_st
        # if time.time() - prog_st > 10:
        #     prog_st = time.time()
        #     await myHeartbeat(ws, heartbeat_message=MESSAGES['HEARTBEAT_MESSAGE'])
        for ws in connections:
            await asyncio.sleep(10)
            await myHeartbeat(ws, heartbeat_message=MESSAGES['HEARTBEAT_MESSAGE'])


connections = []


async def recv_insert(uri, insert_function):
    async with websockets.connect(uri) as ws:
        connections.append(ws)
        if await myLogin(websocket=ws):
            await ws.send(MESSAGES['SUBSCRIBE_MESSAGE'])
            if ws.closed:
                print("connection is closed")
            while True:
                try:

                    message_str = await ws.recv()
                    message = json.loads(message_str)

                    response = create_fxplux_response(message)
                    if response is not None:
                        await insert_function(response)
                    else:
                        print('response is None')
                except Exception as e:
                    print('recv_insert error is raised ;')
                    print(e)


async def get_async_fxplus_v2(*, insert_function):
    loop = asyncio.get_event_loop()

    try:
        asyncio.ensure_future(recv_insert(uri='wss://websocket.foreks.com/websocket', insert_function=insert_function))
        asyncio.ensure_future(send_heartbeat())
        loop.run_forever()
        # asyncio.ensure_future(recv_insert(ws, insert_function))
        # loop.run_until_complete()
    except Exception as e:
        print('hata: ', str(e))
    # while True:

    # await send_heartbeat(ws)
    # await recv_insert(ws, insert_function)

    # if time.time() - program_starts > 10:
    #     program_starts = time.time()
    #     await myHeartbeat(ws, heartbeat_message=MESSAGES['HEARTBEAT_MESSAGE'])
    # else:
    #     print('not ')


async def get_async_fxplus(*, insert_function):
    uri = 'wss://websocket.foreks.com/websocket'

    async with websockets.connect(uri, ping_interval=14) as ws:
        connections.append(ws)
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
