import stores.albert as albert
import stores.kaufland as kaufland
import stores.lidl as lidl
import stores.tesco as tesco
from models.models import *
from playwright.async_api import async_playwright
from dataclasses import asdict
import json
import traceback

JSON_PATH = 'data/listings.json'
RETRIES = 3

async def fetch_listings() -> list[StoreInventory]:
    for i in range(RETRIES):
        try:
            async with async_playwright() as p:
                browser = await p.firefox.launch(headless=True)
    
                listings = []
                listings.append(await albert.get_listings(browser))
                listings.append(await kaufland.get_listings(browser))
                listings.append(await lidl.get_listings(browser))
                listings.append(await tesco.get_listings(browser))

                for store in listings:
                    store.beers.sort()
                listings.sort()
                await browser.close()
                return listings
        except Exception:
            traceback.print_exc()
            if i < RETRIES - 1:
                print('fetching listings failed, retrying')
            else:
                raise

async def update_listings() -> list[dict]:
    listings = await fetch_listings()
    serialized_listings = [listing.model_dump(mode='json') for listing in listings]

    with open(JSON_PATH, 'w') as file:
        file.write(json.dumps(serialized_listings, ensure_ascii=False, indent=4))
    return serialized_listings