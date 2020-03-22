from websocket.export_libraries import *
from websocket.variables import *

data = []


async def login(uri, websocket):
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


x = pd.DataFrame(data)
x.columns = list(map(lambda col: inv_d_lookup[col], x.columns))
