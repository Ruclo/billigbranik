from enum import Enum

class BeerType(str, Enum):
    LEZAK_10 = "10° ležák"
    VYCEPNI_10 = "10° výčepní"
    LEZAK_11 = "11° ležák"

class ContainerType(str, Enum):
    PET = "pet"
    GLASS = "glass"
    CAN = "can"