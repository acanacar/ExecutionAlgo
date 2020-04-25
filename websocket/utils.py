import time
import asyncpg
import logging
from asyncpg.pool import Pool

logger = logging.getLogger('websockets')
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


async def create_pool(*, dsn: str, min_conn: int = 2, max_conn: int = 10, **kwargs) -> Pool:
    pool = await asyncpg.create_pool(dsn=dsn,
                                     min_size=min_conn,
                                     max_size=max_conn,
                                     **kwargs)
    logger.info("Pool created")
    return pool


def get_pool(dsn, loop):
    attempts = 20
    sleep_between_attempts = 3
    for _ in range(attempts):
        try:
            pool = loop.run_until_complete(create_pool(dsn=dsn))
        except Exception as e:
            logger.exception(e)
            time.sleep(sleep_between_attempts)
        else:
            return pool

    raise Exception(f"Could not connect to database using {dsn} after "
                    f"{attempts * sleep_between_attempts} seconds")
#
#
# import asyncio
#
#
# def hello_world(loop):
#     """A callback to print 'Hello World' and stop the event loop"""
#     print('Hello World')
#     loop.stop()
#
#
# loop = asyncio.get_event_loop()
#
# # Schedule a call to hello_world()
# loop.call_soon(hello_world, loop)
#
# # Blocking call interrupted by loop.stop()
# try:
#     loop.run_forever()
# finally:
#     loop.close()
#
# import asyncio
# import datetime
#
#
# def display_date(end_time, loop):
#     print(datetime.datetime.now())
#     if (loop.time() + 1.0) < end_time:
#         loop.call_later(1, display_date, end_time, loop)
#     else:
#         loop.stop()
#
#
# loop = asyncio.get_event_loop()
#
# # Schedule the first call to display_date()
# end_time = loop.time() + 5.0
# loop.call_soon(display_date, end_time, loop)
#
# # Blocking call interrupted by loop.stop()
# try:
#     loop.run_forever()
# finally:
#     loop.close()
