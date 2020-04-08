import asyncio
from asyncpg.pool import *
from collections import namedtuple
import asyncpg


async def insert_ticker(*, pool: Pool, table: str) -> None:
    # fields = msg.keys()
    # placeholders = sd
    pass


async def run():
    conn = await asyncpg.connect(user='acanacar', password='50355035',
                                 database='acanacar', host='127.0.0.1')
    values = await conn.fetch('''
    SELECT * 
    FROM playground  where color='blue'
    ''')
    # WHERE color="blue"
    print(values)
    await conn.close()


loop = asyncio.get_event_loop()
loop.run_until_complete(run())


async def create_table_weather(conn, table_name='weather'):
    await conn.execute(
        f""" CREATE TABLE {table_name} (
        id      serial PRIMARY KEY,
        city    varchar(80),
        temp_lo int,  --low temperature
        temp_hi int,  --high temperature
        prcp    real, --precipitation
        date    date ); """)


async def create_table_cities(conn, table_name='cities'):
    await conn.execute(
        f""" CREATE TABLE {table_name} ( id serial PRIMARY KEY, name varchar(80), location point); """)


async def run_weather():
    connection = await asyncpg.connect(user='acanacar', password='50355035',
                                       database='acanacar', host='127.0.0.1')
    await create_table_weather(conn=connection, table_name='weatherdeneme2')
    await create_table_cities(conn=connection, table_name='citiesdeneme')

    await connection.close()


loop = asyncio.get_event_loop()
loop.run_until_complete(run_weather())


async def insert_weather(connection, table_name, table_values=(1, 2, 3)):
    try:
        await connection.execute(f"INSERT INTO {table_name} VALUES {table_values}")
    except asyncpg.exceptions.InvalidTextRepresentationError as e:
        print(f"InvalidTextRepresentationError -> {e}")


async def main():
    connection = await asyncpg.connect(user='acanacar', password='50355035',
                                       database='acanacar', host='127.0.0.1')
    await insert_weather(connection=connection,
                         table_name='weatherdeneme2',
                         table_values=('San Francisco', 43, 57, 0, 0, '1994-11-29'))


loop = asyncio.get_event_loop()
loop.run_until_complete(main())

import pandas as pd
from constants import *

from sqlalchemy import create_engine
from sqlalchemy.schema import DropTable

engine = create_engine('postgresql://acanacar:50355035@localhost:5432/acanacar')
DropTable()
df = pd.read_pickle(websocket_path / Path('outputs/data_sample_5.pickle'))
df.columns = [str.lower(col) for col in df.columns]
df.rename(columns={'datetime': 'datetime_pd', 'mydatetime': 'my_time_pd'}, inplace=True)

df.to_sql('time_series_5', engine)

result_set = engine.execute("SELECT * FROM table_name")
for result in result_set:
    print(result)

import datetime
current_milli_time = lambda: int(round(datetime.time() * 1000))


async def insert_ticker(connection, table_name='table_name'):
    try:
        ts = current_milli_time()
        my_time_pd = pd.to_datetime(ts, unit='ms')
        row = (3, 1.0, "xy", ts, my_time_pd)
        print(row)
        await connection.execute(f"""INSERT INTO {table_name} (_id,last,_i,my_time,datetime_pd) VALUES {row}""")
    except asyncpg.exceptions.InvalidTextRepresentationError as e:
        print(f"InvalidTextRepresentationError -> {e}")


async def changeTableColumnType(connection, table_name='table_name'):
    try:
        await connection.execute(f"""
        ALTER TABLE {table_name}
        ALTER COLUMN DateTime TYPE INT;
        """)
    except Exception as e:
        print(str(e))


async def checkTableColumns(connection, table_name='table_name'):
    try:
        columns = await connection.execute(f"""
                    SELECT COLUMN_NAME
                    FROM information_schema.COLUMNS
                    WHERE TABLE_NAME = 'time_series_5';""")
        # await connection.execute(f"""
        # SELECT column_name FROM INFORMATION_SCHEMA.COLUMNS WHERE table_name = {table_name}
        # """)
        print(columns)
        return columns
    except Exception as e:
        print(str(e))


async def main():
    connection = await asyncpg.connect(user='acanacar', password='50355035',
                                       database='acanacar', host='127.0.0.1')
    await insert_ticker(connection=connection, table_name='time_series_5')
    # await changeTableColumnType(connection, table_name='time_series_5')
    # columns = await checkTableColumns(connection, table_name='time_series_5')
    # print(columns)


loop = asyncio.get_event_loop()
loop.run_until_complete(main())

