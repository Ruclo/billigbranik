import re
from playwright.async_api import async_playwright
import asyncio
from models.models import *
from models.enums import *
from unicodedata import normalize, combining
from utils.beer_type_extractor import extract_beer_type

BASE_URL = 'https://nakup.itesco.cz'
URL = BASE_URL + '/groceries/cs-CZ/search?query=branik'

async def extract_listing_info(browser, url: str) -> BeerListing:
    page = await browser.new_page()
    await page.goto(url)

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

    product_title = await page.locator("h1.product-details-tile__title").first.inner_text()

    description = product_title + await page.locator('div#product-description').inner_text()
    beer_type = extract_beer_type(description)
    
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

    listing = BeerListing(type=beer_type, container=container, volume_l=volume, price_czk=price)
    if units is not None:
        listing.units = int(units)

    return listing


async def get_listings(browser) -> StoreInventory:

    page = await browser.new_page()
    await page.goto(URL)

    inventory = StoreInventory(store='Tesco')
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
