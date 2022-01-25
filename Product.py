import math

from Enums.Condition import Condition, Conditions
from Enums.Price import Price, PriceType, Consts
from Enums.Rarity import Rarity


class Product:
    title: str
    product_name: str
    set_name: str
    product_line: str
    tcgplayer_id: str
    number: str
    rarity: Rarity
    condition: Condition
    market_price: Price
    photo_url: str
    direct_low_price: Price
    low_price_with_shipping: Price
    low_price: Price
    total_quantity: int
    add_to_quantity: int
    marketplace_price: Price

    def __init__(self, tcgplayer_id: str, product_line: str, set_name: str, product_name: str, title: str, number: str,
                 rarity: str, condition: str, market_price: str, direct_low_price: str,
                 low_price_with_shipping: str, low_price: str, total_quantity: int, add_to_quantity: int,
                 marketplace_price: str, photo_url: str):
        self.marketplace_price = Price(marketplace_price)
        self.add_to_quantity = add_to_quantity
        self.total_quantity = total_quantity
        self.low_price = Price(low_price)
        self.low_price_with_shipping = Price(low_price_with_shipping)
        self.direct_low_price = Price(direct_low_price)
        self.photo_url = photo_url
        self.market_price = Price(market_price)
        self.condition = Condition(condition)
        if self.condition.condition is Conditions.UNOPENED:
            self.rarity = Rarity.PRODUCT
        else:
            self.rarity = Rarity(rarity)
        self.number = number
        self.tcgplayer_id = tcgplayer_id
        self.product_line = product_line
        self.set_name = set_name
        self.product_name = product_name
        self.title = title

    def __str__(self) -> str:
        return f'{self.total_quantity}x {self.set_name}: {self.product_name} - ' \
               f'{self.condition.condition.value} {self.condition.finish.value} - {self.marketplace_price.price}'

    def to_row(self) -> list:
        if self.marketplace_price.type is PriceType.NONE:
            print(f'{self} has no price set. Defaulting it to {Consts.SYP_DEFAULT_PRICE}, '
                  f'you should modify that in the output CSV')
            marketplace_price = Consts.SYP_DEFAULT_PRICE
        else:
            marketplace_price = self.marketplace_price.price
        return [
            self.tcgplayer_id,
            self.product_line,
            self.set_name,
            self.product_name,
            self.title,
            self.number,
            self.rarity.value,
            self.condition.string,
            self.market_price.price,
            self.direct_low_price.price,
            self.low_price_with_shipping.price,
            self.low_price.price,
            self.total_quantity,
            self.add_to_quantity,
            marketplace_price,
            self.photo_url
        ]

    def round_to_99_cents(self):
        if self.marketplace_price.type is PriceType.SOME:
            self.marketplace_price.price = math.ceil(self.marketplace_price.price) - 0.01

    def to_direct_low_with_multiplier(self, multiplier: float = 1.0):
        if self.direct_low_price.type is PriceType.SOME:
            self.marketplace_price = Price(self.direct_low_price.price * multiplier)

    def to_low_with_shipping_with_multiplier(self, multiplier: float = 1.0):
        if self.low_price_with_shipping.type is PriceType.SOME:
            self.marketplace_price = Price(self.low_price_with_shipping.price * multiplier)
