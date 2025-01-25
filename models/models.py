from pydantic import BaseModel, Field, computed_field
from typing import List
from .enums import BeerType, ContainerType
from decimal import Decimal


class BeerListing(BaseModel):
    type: BeerType
    container: ContainerType
    volume_l: Decimal
    price_czk: Decimal
    units: int = 1

    @computed_field
    @property
    def price_per_liter(self) -> Decimal:
        total_volume = self.volume_l * Decimal(self.units)
        price_per_liter = self.price_czk / total_volume
        return price_per_liter.quantize(Decimal('0.01'))
    

    def __lt__(self, other: 'BeerListing') -> bool:
        return self.price_per_liter < other.price_per_liter



class StoreInventory(BaseModel):
    store: str
    beers: List[BeerListing] = Field(default_factory=list)

    #assumes field beers is sorted
    def __lt__(self, other: 'StoreInventory') -> bool:
        if not self.beers:
            return True

        if not other.beers:
            return False

        return self.beers[0] < other.beers[0]