from dataclasses import dataclass, field
from typing import List
from .enums import BeerType, ContainerType
from decimal import Decimal

@dataclass
class BeerListing:
    type: BeerType
    container: ContainerType
    volume_l: Decimal
    price_czk: Decimal
    units: int = field(default=1)

    @property
    def price_per_liter(self) -> Decimal:
        return round(self.price_czk / self.volume_l, 2)

@dataclass
class StoreInventory:
    store: str
    beers: List[BeerListing] = field(default_factory=list)

    def get_cheapest_beer(self) -> BeerListing:
        return min(self.beers, key=lambda beer: beer.price_per_liter)