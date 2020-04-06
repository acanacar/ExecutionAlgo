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
        # msg['my_date'] = pd.to_datetime(time.time(), unit='s')
        msg['my_time'] = current_milli_time()
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
