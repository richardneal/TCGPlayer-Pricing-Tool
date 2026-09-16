# Copyright (c) 2022, Richard Neal
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.
from __future__ import annotations

from decimal import Decimal

from Enums.Condition import Condition, Conditions
from Enums.Headers import Headers
from Enums.Price import Price, SYP_DEFAULT_PRICE, round_up_to_99_cents
from Enums.Rarity import Rarity

# Reprices that would move a price by more than this fraction are reported and
# skipped, so that one bad day of TCGPlayer data cannot rewrite a whole
# inventory unattended. Set it to None to apply every reprice regardless of size.
MAX_PRICE_CHANGE = Decimal('0.5')


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
        self.add_to_quantity = int(add_to_quantity)
        self.total_quantity = int(total_quantity)
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

    def __str__(self):
        description = f'{self.total_quantity}x {self.set_name}: {self.product_name} - ' \
                      f'{self.condition.condition.value}'
        if self.condition.finish.value:
            description += f' {self.condition.finish.value}'
        if self.marketplace_price:
            description += f' - ${self.marketplace_price}'
        return description

    def to_row(self) -> list:
        # Keyed by header rather than positional, so that the row can never fall
        # out of step with the header row that output_csv writes from Headers.
        values = {
            Headers.TCGPLAYER_ID: self.tcgplayer_id,
            Headers.PRODUCT_LINE: self.product_line,
            Headers.SET_NAME: self.set_name,
            Headers.PRODUCT_NAME: self.product_name,
            Headers.TITLE: self.title,
            Headers.NUMBER: self.number,
            Headers.RARITY: self.rarity.value,
            Headers.CONDITION: self.condition.string,
            Headers.MARKET_PRICE: self.market_price.to_csv(),
            Headers.DIRECT_LOW_PRICE: self.direct_low_price.to_csv(),
            Headers.LOW_PRICE_WITH_SHIPPING: self.low_price_with_shipping.to_csv(),
            Headers.LOW_PRICE: self.low_price.to_csv(),
            Headers.TOTAL_QUANTITY: self.total_quantity,
            Headers.ADD_TO_QUANTITY: self.add_to_quantity,
            # Never write a blank price back to TCGPlayer, even if price_products
            # was not run first.
            Headers.MARKETPLACE_PRICE: (self.marketplace_price or Price(SYP_DEFAULT_PRICE)).to_csv(),
            Headers.PHOTO_URL: self.photo_url,
        }
        return [values[header] for header in Headers]

    def percent_change_to(self, new_price: Price) -> Decimal | None:
        if not self.marketplace_price:
            return None
        return (new_price.or_zero() - self.marketplace_price.price) * 100 / self.marketplace_price.price

    def reprice(self, new_price: Price, multiplier: Decimal = Decimal(1), round_to_99_cents: bool = False):
        if not new_price:
            return

        if round_to_99_cents:
            new_price = Price(round_up_to_99_cents(new_price.price * multiplier))
        else:
            new_price = Price(new_price.price * multiplier)

        if new_price == self.marketplace_price:
            return

        percent_change = self.percent_change_to(new_price)
        if percent_change is None:
            change_description = 'no previous price'
        else:
            change_description = f'a {percent_change.quantize(Decimal("0.1"))}% difference'

        if MAX_PRICE_CHANGE is not None and percent_change is not None \
                and abs(percent_change) > MAX_PRICE_CHANGE * 100:
            print(f'Leaving {self} alone: ${new_price} would be {change_description}, over the '
                  f'{MAX_PRICE_CHANGE * 100:.0f}% limit. Reprice it by hand if that is correct.')
            return

        if self.total_quantity > 0:
            print(f'Repricing {self} to ${new_price} ({change_description})')
        self.marketplace_price = new_price


def get_total_price(products: list[Product]) -> Decimal:
    total = sum((product.marketplace_price.or_zero() * product.total_quantity for product in products), Decimal(0))
    return total.quantize(Decimal('0.01'))
