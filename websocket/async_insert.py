from websocket.export_libraries import *
from websocket.connection_api import get_async_fxplus, handle_fxplus
from websocket.utils import get_pool
from websocket.insert import insert_ticker
from postgreSQL_db.config import config

params = config()


def main():
    '''postgres://user:pass@host:port/database?option=value'''
    dsn = f'postgres://{params["user"]}:{params["password"]}@{params["host"]}:5432/{params["database"]}'
    while True:
        pool = get_pool(dsn, asyncio.get_event_loop())
        insert_ticker_async = lambda response: insert_ticker(message=response, pool=pool, table='time_series_5')

        loop = asyncio.get_event_loop()
        loop.run_until_complete(handle_fxplus(insert_function=insert_ticker_async, pool=pool))
        loop.run_forever()

        asyncio.get_event_loop().run_until_complete(pool.close())


if __name__ == '__main__':
    main()
