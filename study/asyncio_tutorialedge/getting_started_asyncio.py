import asyncio

async def myCoroutine():
    print("Simple Event Loop Example")


def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(myCoroutine())
    loop.close()


if __name__ == '__main__':
    main()

# Coroutines

import asyncio


async def myFunc1():
    print("Coroutine 1")


@asyncio.coroutine
def myFunc2():
    print("Coroutine 2")


# Futures

import asyncio


async def myCoroutine(future):
    await asyncio.sleep(1)

    future.set_result("My coroutine-turned-future has completed")


async def main():
    future = asyncio.Future()
    await asyncio.ensure_future(myCoroutine(future))

    print(future.result())


loop = asyncio.get_event_loop()

try:
    loop.run_until_complete(main())
finally:
    loop.close()


# Multiple Coroutines

import asyncio
import random

async def myCoroutine(id):
    process_time = random.randint(1,5)
    await asyncio.sleep(process_time)
    print(f"Coroutine: {id}, has successfully completed after {process_time} seconds")

async def main():
    tasks = []
    for i in range(10):
        tasks.append(asyncio.ensure_future(myCoroutine(i)))

    await asyncio.gather(*tasks)


loop = asyncio.get_event_loop()
try:
    loop.run_until_complete(main())
finally:
    loop.close()