from models.enums import BeerType
from unicodedata import combining, normalize

def extract_beer_type(description):
    beer_type = None
    description = ''.join(c for c in normalize('NFKD', description) if not combining(c)).lower()

    if '11' in description or 'jedenactka' in description:
        beer_type = BeerType.LEZAK_11
    elif 'lezak' in description:
        beer_type = BeerType.LEZAK_10
    elif 'vycepni' in description:
        beer_type = BeerType.VYCEPNI_10
    else:
        beer_type = BeerType.VYCEPNI_10
        print('Unknown type detected in', description)
    return beer_type