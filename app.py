from tasks.fetch_listings import update_listings
from asyncio import run

async def main():
    print(await update_listings())

if __name__ == '__main__':
    run(main())