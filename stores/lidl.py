import re
from playwright.async_api import async_playwright
import asyncio
from models.models import *
from models.enums import *
from unicodedata import normalize, combining
from datetime import datetime
from zoneinfo import ZoneInfo

BASE_URL = 'https://lidl.cz'
URL = BASE_URL + '/q/search?q=branik'
TIMEZONE_CZECH = ZoneInfo("Europe/Prague")

async def extract_listing_info(browser, url) -> BeerListing:
   pass

async def get_listings(browser) -> StoreInventory:
   page = await browser.new_page()
   await page.goto(URL)

   inventory = StoreInventory("Lidl")

   await page.wait_for_selector('.s-loading')

   ol = page.locator('ol#s-results')

   if not await ol.is_visible():
      await page.close()
      return inventory
   
   list_items = await ol.locator('li:not(.s-grid__item--hidden)').all()
   hrefs = set()
   for li in list_items:
      span = await li.locator('.ods-badge__label').first.inner_text()
      dates = re.search(r'(\d{1,2}.\d{1,2}.)\s*-\s*(\d{1,2}.\d{1,2}.)', span)
      if dates:
         sale_start_date = datetime.strptime(f"{dates.group(1)}{datetime.now().year}", "%d.%m.%Y").replace(tzinfo=TIMEZONE_CZECH)
         current_date = datetime.now(TIMEZONE_CZECH)
         if current_date < sale_start_date:
            continue
      hrefs.add(BASE_URL + await li.locator('a').first.get_attribute('href'))

   await page.close()
   
   tasks = [extract_listing_info(browser, link) for link in hrefs]

   listings = await asyncio.gather(*tasks)
   inventory.beers = listings

   



async def main():
   async with async_playwright() as p:
      browser = await p.firefox.launch(headless=True)
      await get_listings(browser)
      
      await browser.close()

if __name__ == '__main__':
   asyncio.run(main())