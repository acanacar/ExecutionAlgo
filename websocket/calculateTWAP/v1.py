from websocket.export_libraries import *
from websocket.utils import get_pool
from postgreSQL_db.config import config
from asyncpg.pool import Pool

params = config()

import asyncio
import asyncpg
import logging

logger = logging.getLogger('websockets')


async def create_pool(*, dsn: str, min_conn: int = 2, max_conn: int = 10, **kwargs) -> Pool:
    pool = await asyncpg.create_pool(dsn=dsn,
                                     min_size=min_conn,
                                     max_size=max_conn,
                                     **kwargs)
    logger.info("Pool created")
    return pool


async def run():
    dsn = f'postgres://{params["user"]}:{params["password"]}@{params["host"]}:5432/{params["database"]}'
    conn_pool = await create_pool(dsn=dsn)
    # conn = await asyncpg.connect(user=params["user"], password=params["password"],
    #                              database=params["database"], host=params["host"])
    queries = [
        ''' SELECT * FROM time_series_5 WHERE _i='o850' ''',
        '''SELECT * FROM time_series_5 WHERE _i='o1698' ''']
    tasks = [
        conn_pool.fetch(queries[0]),
        conn_pool.fetch(queries[1])

    ]
    results = asyncio.gather(*tasks)
    output = await results
    print(output)

loop = asyncio.get_event_loop()
x = loop.run_until_complete(run())
