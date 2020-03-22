import asyncio


@asyncio.coroutine
def py34_coro():
    """Generator-based coroutine"""
    s = yield from stuff()
    return s


async def py35_coro():
    s = await stuff()
    return s


async def stuff():
    return 0x10, 0x20, 0x30


def gen():
    yield 0x10, 0x20, 0x30


g = gen()

from itertools import cycle


def endless():
    """Yields 9, 8, 7, 6, 9, 8, 7, 6, ... forever"""
    yield from cycle((9, 8, 7, 6))


e = endless()
total = 0
for i in e:
    if total < 30:
        print(i, end=" ")
        total += i
    else:
        print()
        # Pause execution. We can resume later.
        break

# Resume
next(e), next(e), next(e)


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

print(g)
print(f)
