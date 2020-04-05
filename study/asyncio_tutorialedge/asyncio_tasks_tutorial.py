
import asyncio
import time


async def myTask():
    time.sleep(1)
    print("Processing Task")


async def myTaskGenerator():
    for i in range(5):
        asyncio.ensure_future(myTask())


loop = asyncio.get_event_loop()
loop.run_until_complete(myTaskGenerator())
print("Completed All Tasks")
loop.close()

import asyncio
import time


async def myTask():
    time.sleep(1)
    print("Processing Task")

    for task in asyncio.Task.all_tasks():
        print(task)
        task.cancel()
        print(task)


async def main():
    for i in range(5):
        asyncio.ensure_future(myTask())


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
print("Completed All Tasks")
loop.close()

import asyncio


async def myWorker(number):
    return number * 2


async def main(coros):
    for fs in asyncio.as_completed(coros):
        print(await fs)


coros = [myWorker(1) for i in range(5)]

try:
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(coros))
except KeyboardInterrupt:
    pass
finally:
    loop.close()

import asyncio


async def myWorker():
    print("Hello World")


async def main():
    print("My Main")


try:
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.gather(*[myWorker() for i in range(5)]))

except KeyboardInterrupt:
    pass

finally:
    loop.close()



import asyncio

async def myWorker():
    print("Hello World")

async def main():
    print("My Main")

try:
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.wait([myWorker() for i in range(5)], timeout=2))
except KeyboardInterrupt:
    pass
finally:
    loop.close()