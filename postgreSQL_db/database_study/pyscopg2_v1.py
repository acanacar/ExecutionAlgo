import psycopg2
from postgreSQL_db.config import config
import time
from collections import namedtuple

table_name = 'timescale_executionalgo_t2'

current_milli_time = lambda: int(round(time.time() * 1000))

row = (12, 11.5, 12.4, current_milli_time())
a = {'last': 75, 'bid': 77, 'ask': 74, 'my_time': current_milli_time()}

# Child = namedtuple('Child',
#                    ['last', 'bid', 'ask', 'my_time'])
#
# c1=Child(75,77,74,current_milli_time())

# sql = f"""-- INSERT INTO {table_name} ({','.join(a.keys())}) VALUES{tuple(a.values())};"""

# sql = f"""INSERT INTO {table_name}(last,bid,ask,my_time) VALUES{row};"""

# sql = f"""ALTER TABLE {table_name} ALTER COLUMN _id TYPE INT;"""

# sql = f"""SELECT * FROM {table_name} ORDER BY datetime DESC LIMIT 10"""

# sql = f"""ALTER TABLE {table_name} RENAME COLUMN bid_ TO bid;"""

# sql = f"""SELECT column_name FROM INFORMATION_SCHEMA.columns
#                      WHERE table_schema = 'public'
#                      AND TABLE_NAME = '{table_name}';"""

sql = f"""SELECT column_name,data_type FROM information_schema.columns
                   WHERE TABLE_NAME = '{table_name}';"""

# sql = f""" CREATE TABLE Execution_Algo_t2 (
#     _id integer,
#     snapshot integer,
#     _i text,
#     datetime_pd timestamp without time zone,
#     datetime bigint,
#     my_time bigint,
#     last double precision,
#     bid double precision,
#     ask double precision
#     ) ;
#     """

try:
    params = config()
    conn = psycopg2.connect(**params)
    cur = conn.cursor()

    cur.execute(sql)

    query_results = cur.fetchall()
    print(query_results)

except psycopg2.ProgrammingError as e:
    print(str(e))

except Exception as e:
    print(str(e))

finally:
    conn.commit()
    cur.close()
    conn.close()
