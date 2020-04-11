import logging
from websocket.variables import *

logger = logging.getLogger(__name__)


def get_query(msg, table):
    query = None
    if msg is not None:

        try:

            # columns_ = ','.join(list(map(lambda col: inverse_fields_lookup[col], cols)))
            # values_ = tuple(map(lambda col: msg.get(col), cols))
            msg_ = {inverse_fields_lookup[key]: value for key, value in msg.items()}
            columns_ = ','.join(msg_.keys())
            values_ = tuple(msg_.values())
            query = f"""INSERT INTO {table} ({columns_}) VALUES{values_};"""

        except Exception as e:
            print(e)
    return query


async def insert_ticker(message, pool, table: str) -> None:
    query = get_query(msg=message, table=table)
    # query = """INSERT INTO time_series_5 (datetime_pd, my_time_pd)
    # VALUES
    # (
    #     -- '2016-06-22 19:10:25-07',
    #     '2020-04-08 11:38:55.167000',
    #     '2016-06-22 19:10:25-07'
    # );
    # """
    if query is not None:
        async with pool.acquire() as connection:
            async with connection.transaction():
                try:
                    await connection.execute(query)
                except Exception as e:
                    print(str(e))
