from dev.export_libraries import *
from oop_study.oop_dev.ALGO_STORAGES import VAR_STORAGES, QUEUE_STORAGES, ORDER_STORAGES
from oop_study.oop_dev.subscription import subscribe
from oop_study.oop_dev.task_total import TASK_TOTAL
from oop_study.oop_dev.websocket_conn import conn, heartbeat

VAR_STORAGES = VAR_STORAGES()


async def main():
    websocket = await conn(VAR_STORAGES.MESSAGES)

    asyncio.create_task(heartbeat(websocket, VAR_STORAGES.MESSAGES))
    # await subscribe_(websocket, VAR_STORAGES.MESSAGES['SUBSCRIBE_MESSAGE'])
    # await subscribe2(websocket, VAR_STORAGES.MESSAGES['SUBSCRIBE_MESSAGE'])
    await subscribe(websocket=websocket,
                    symbol='H1728',
                    fields=VAR_STORAGES.shortcodes['last'])
    taskk = TASK_TOTAL(ws=websocket,
                       var_storages=VAR_STORAGES,
                       queue_storages=QUEUE_STORAGES,
                       order_storages=ORDER_STORAGES)


loop = asyncio.get_event_loop()
loop.run_until_complete(main())

loop.run_forever()
