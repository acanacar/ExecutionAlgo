import psycopg2
from websocket.config import config

table_name = 'time_series_5'

params = config()
conn = psycopg2.connect(**params)
cur = conn.cursor()

table_name = 'time_series_5'
# cur.execute("""SELECT * FROM time_series_5""")
# cur.execute(f"""ALTER TABLE time_series_5 ALTER COLUMN datetime TYPE BIGINT;""")

cur.execute(f"""SELECT column_name FROM information_schema.columns
                WHERE table_schema = 'public'
                AND TABLE_NAME = {table_name};""")

query_results = cur.fetchall()
print(query_results)

cur.close()
conn.close()
