from enum import Enum


class PriceType(Enum):
    NONE = 1
    SOME = 2


class Consts(Enum):
    PRICE_FLOOR = 0.01
    SYP_DEFAULT_PRICE = 999.99


class Price:
    type: PriceType
    price: float

    def __init__(self, price: str | float):
        if price:
            price = float(price)
        else:
            price = 0.0

        if price < Consts.PRICE_FLOOR.value or price == Consts.SYP_DEFAULT_PRICE.value:
            self.type = PriceType.NONE
            self.price = 0.0
        else:
            price = float(price)
            self.type = PriceType.SOME
            self.price = price