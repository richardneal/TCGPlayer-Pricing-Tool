import math
from enum import Enum


class PriceType(Enum):
    NONE = 1
    SOME = 2


class Price:
    price_type: PriceType
    price: float

    def __init__(self, price: str | float):
        if isinstance(price, str):
            if price == '' or float(price) < 0.01:
                self.price_type = PriceType.NONE
                self.price = 0.0
            else:
                self.price_type = PriceType.SOME
                self.price = float(price)
        else:
            if price < 0.01:
                self.price_type = PriceType.NONE
                self.price = 0.0
            else:
                self.price_type = PriceType.SOME
                self.price = price

