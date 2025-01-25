from models.models import *
from models.enums import *
from utils.beer_type_extractor import extract_beer_type
import re
from playwright.async_api import async_playwright
import asyncio
from unicodedata import normalize, combining

URL = 'https://prodejny.kaufland.cz/nabidka/aktualni-tyden/pivo-v-akci.html'

async def get_listings(browser) -> StoreInventory:
   page = await browser.new_page()
   await page.goto(URL)

   items = await page.locator('.k-product-tile').all()
   inventory = StoreInventory(store='Kaufland')

   for item in items:
      description = await item.locator('.k-product-tile__text').first.inner_text()
      description = ''.join(c for c in normalize('NFKD', description) if not combining(c)).lower()
      if 'branik' not in description:
         continue
      
      beer_type = extract_beer_type(description)

      container_type = None
      if 'pet' in description:
         container_type = ContainerType.PET
      elif 'plech' in description:
         container_type = ContainerType.CAN
      else:
         container_type = ContainerType.GLASS
      
      volume_info = await item.locator('.k-product-tile__unit-price').first.inner_text()
      volume = Decimal(re.search(r'(\d+[.,]?\d*)\s*l', volume_info).group(1).replace(',', '.'))

      discount_info = item.locator('k-price-tag--k-card')
      price_info = None
      if await discount_info.first.is_visible():
         price_info = await discount_info.locator('.k-price-tag__price').first.inner_text()
      else:
         price_info = await item.locator('.k-price-tag__price').first.inner_text()
      
      price = Decimal(price_info.replace(',', '.'))

      listing = BeerListing(type=beer_type, container=container_type, volume_l=volume, price_czk=price)
      inventory.beers.append(listing)
         
   await page.close()
   return inventory
        

async def main():
   async with async_playwright() as p:
      browser = await p.firefox.launch(headless=True)
      await get_listings(browser)
      
      await browser.close()

if __name__ == '__main__':
   asyncio.run(main())