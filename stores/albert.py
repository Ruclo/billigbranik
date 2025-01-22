import re
import asyncio
from models.models import *
from models.enums import *
from playwright.async_api import async_playwright
from unicodedata import normalize, combining

BASE_URL = 'https://www.albert.cz'
URL = BASE_URL + '/search-results?q=branik%3Arelevance&sort=relevance'

async def extract_listing_info(browser, link) -> BeerListing:
    container = None
    if 'Lahve' in link:
        container = ContainerType.GLASS
    elif 'Plechovky' in link:
        container = ContainerType.CAN
    elif 'Pet' in link:
        container = ContainerType.PET
    else:
        container = ContainerType.GLASS
        print("Warning, unknown type in link:", link)

    page = await browser.new_page()
    await page.goto(link)
    await page.get_by_test_id("product-details-section").wait_for(timeout = 30000)

    price_div = page.get_by_test_id("product-block-price")
    main_price = await price_div.locator("div").nth(1).inner_text()
    sup_price = await price_div.locator("sup").inner_text()

    price = Decimal(main_price + '.' + sup_price)
    
    volume_tag = await page.get_by_test_id("product-block-supplementary-price-2").first.inner_text()
    volume_tag = volume_tag.replace(',', '.')

    matches = re.findall(r'\d+.?\d*', volume_tag)
    volume = Decimal(matches[0])

    product_name = await page.get_by_test_id("product-common-header-title").inner_text()
    product_name = ''.join(c for c in normalize('NFKD', product_name) if not combining(c)).lower()

    beer_type = None
    if '11' in product_name:
        beer_type = BeerType.LEZAK_11
    elif 'lezak' in product_name:
        beer_type = BeerType.LEZAK_10
    elif 'vycepni' in product_name:
        beer_type = BeerType.VYCEPNI_10
    else:
        print('Unknown beer type in ' + product_name)
        beer_type = BeerType.VYCEPNI_10
    

    await page.close()
    bl = BeerListing(beer_type, container, volume, price)
    print(bl)
    return bl


async def get_listings(browser) -> StoreInventory:
    page = await browser.new_page()
    await page.goto(URL)

    inventory = StoreInventory("Albert")
    
    try:
        await page.get_by_test_id("total-products-desktop-info").wait_for(timeout = 30000)
        #await page.wait_for_selector("li.product-item", timeout=15000)
    except TimeoutError:
        print("No result found in albert")
        return inventory

    list_items = await page.locator("li.product-item").all()
    anchors = [item.locator("a").first for item in list_items]
    hrefs = set([BASE_URL + await anchor.get_attribute("href") for anchor in anchors])

    await page.close()
    print(hrefs)

    tasks = [extract_listing_info(browser, link) for link in hrefs]
    listings = await asyncio.gather(*tasks)

    inventory.beers = listings

    return inventory




async def main():
    async with async_playwright() as p:
        browser = await p.firefox.launch(headless=True)

        listings = await get_listings(browser)

        print(listings)
        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())