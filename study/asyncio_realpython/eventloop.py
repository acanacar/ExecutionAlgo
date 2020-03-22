import asyncio

async def main():
    print('hello')
    await asyncio.sleep(.1)
    print('world')

routine = main()
routine