import re
from playwright.async_api import async_playwright
import asyncio

async def scrape_product(browser, url: str) -> dict[str, str]:
    price_str = None
    amount_str = None

    page = await browser.new_page()
    await page.goto(url)

    price_div = await page.wait_for_selector('div.price-per-sellable-unit')
    amount_div = await page.query_selector('div#pack-size')
    amount_str = await amount_div.text_content()
    
    discount_span = await page.query_selector('span.offer-text')
    if discount_span:
        price_str = await discount_span.text_content()
    else:
        price_str = await price_div.text_content()


    price_pattern = r'(\d+[.,]?\d*)\s*(K[cč]{1})?'

    
    matches = re.findall(price_pattern, price_str, re.IGNORECASE)

    price = None
    for match in matches:
        match = match[0].replace(',', '.')
        if price is None or match < price:
            price = match

    match = re.search(r'(\d+(\.\d+)?l)', amount_str)
    return {match.group(0): price}
    


async def get_prices() -> dict[str, str]:
    branik_links = [
        'https://nakup.itesco.cz/groceries/cs-CZ/products/2001000112197',
        'https://nakup.itesco.cz/groceries/cs-CZ/products/2001019165245',
        'https://nakup.itesco.cz/groceries/cs-CZ/products/2001010175052'

    ]
    dic = {}
    results = []

    async with async_playwright() as p:
        browser = await p.firefox.launch(headless=True)

        tasks = [scrape_product(browser, link) for link in branik_links]
        results = await asyncio.gather(*tasks)

        await browser.close()
    
    for extracted_price in results:
        if not extracted_price:
            continue
        
        for size, price in extracted_price.items():
            if size not in dic or price < dic[size]:
                dic[size] = price
    

    return dic

if __name__ == '__main__':
    asyncio.run(get_prices())
