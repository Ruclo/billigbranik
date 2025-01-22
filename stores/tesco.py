import re
from playwright.async_api import async_playwright
import asyncio
from models.models import *
from models.enums import *
from unicodedata import normalize, combining

BASE_URL = 'https://nakup.itesco.cz'
URL = BASE_URL + '/groceries/cs-CZ/search?query=branik'

async def extract_listing_info(browser, url: str) -> BeerListing:
    page = await browser.new_page()
    await page.goto(url)

    product_title = await page.locator("h1.product-details-tile__title").first.inner_text()
    product_title = ''.join(c for c in normalize('NFKD', product_title) if not combining(c)).lower()

    offer_span = page.locator("span.offer-text").first

    price = None
    if await offer_span.is_visible():
        offer_text = await offer_span.inner_text()
        matches = re.findall(r'(\d+[.,]?\d*)\s*K[cč]', offer_text, re.IGNORECASE)
        for match in matches:
            match = match.replace(',', '.')
            match = Decimal(match)
            if price is None or match < price:
                price = match
    else:
        price_text = await page.locator('.price-control-wrapper .value').first.inner_text()
        price_text = price_text.replace(',', '.')
        price = Decimal(price_text)

    beer_type = None
    if 'jedenactka' in product_title or '11' in product_title:
        beer_type = BeerType.LEZAK_11
    else:
        description = await page.locator('div#product-description').inner_text()
        description = ''.join(c for c in normalize('NFKD', description) if not combining(c)).lower()
        beer_type = BeerType.LEZAK_10 if 'lezak' in description else BeerType.VYCEPNI_10
    
    volume_text = await page.locator("div#net-contents").inner_text()
    match = re.search(r'((\d+)\s*x)?\s*(\d+[.,]?\d*)\s*l', volume_text)
    units = match.group(2)
    volume = Decimal(match.group(3).replace(',', '.'))

    deposit_info = page.locator('div#deposit-info')

    container = None
    if await deposit_info.is_visible():
        container = ContainerType.GLASS
    else:
        container = ContainerType.CAN if volume < 1 else ContainerType.PET

    await page.close()

    listing = BeerListing(beer_type, container, volume, price)
    if units is not None:
        listing.units = units

    return listing


async def get_listings(browser) -> StoreInventory:

    page = await browser.new_page()
    await page.goto(URL)

    inventory = StoreInventory('Tesco')
    await page.wait_for_selector('.results-page')

    anchors = await page.locator("a.product-image-wrapper").all()
    hrefs = set([BASE_URL + await anchor.get_attribute("href") for anchor in anchors])
    print(hrefs)
    await page.close()

    tasks = [extract_listing_info(browser, link) for link in hrefs]

    listings = await asyncio.gather(*tasks)
    print(listings)
    inventory.beers = listings
    return inventory

async def main():
    async with async_playwright() as p:
        browser = await p.firefox.launch(headless=True)
        await get_listings(browser)

        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
