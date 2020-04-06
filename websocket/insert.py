import logging
from websocket.variables import *
logger = logging.getLogger(__name__)


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
    if query is not None:
        async with pool.acquire() as connection:
            async with connection.transaction():
                await connection.execute(query)
