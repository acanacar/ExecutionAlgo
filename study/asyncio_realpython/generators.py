import asyncio

async def mygen(u: int = 10):
    """Yields power of 2 """
    i = 0
    while i < u:
        yield 2 ** i
        i += 1
        await asyncio.sleep(0.1)


async def main():
    g = [i async for i in mygen()]
    f = [j async for j in mygen() if not (j // 3 % 5)]
    return g, f


loop = asyncio.get_event_loop()
g, f = loop.run_until_complete(main())
