import asyncio


async def coro(seq) -> list:
    await asyncio.sleep(max(seq))
    return list(reversed(seq))


async def main():
    t = asyncio.ensure_future(coro([3, 2, 1]))
    await t
    print(f't: type {type(t)}')
    print(f't done: {t.done()}')


loop = asyncio.get_event_loop()
t = loop.run_until_complete(main())
