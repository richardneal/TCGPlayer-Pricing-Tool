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

# Off by default: every reprice is applied, however large. Set a percentage here
# (50 is a reasonable starting point) or pass --max-change to have reprices over
# that size reported and skipped instead, so that one bad day of TCGPlayer data
# cannot rewrite a whole inventory unattended.
MAX_PRICE_CHANGE: Decimal | None = None

# When a limit is in force, it only applies once there is real money in it. A
# cheap card going from $1.98 to $2.99 is over any sane percentage while being a
# dollar, and holding those back buries the changes actually worth looking at.
MIN_PRICE_CHANGE_TO_SKIP = Decimal('5')


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

    @property
    def description(self) -> str:
        """What the product is, without its price, for messages that state a price themselves."""
        description = f'{self.total_quantity}x {self.set_name}: {self.product_name} - ' \
                      f'{self.condition.condition.value}'
        if self.condition.finish.value:
            description += f' {self.condition.finish.value}'
        return description

    def __str__(self):
        if self.marketplace_price:
            return f'{self.description} - ${self.marketplace_price}'
        else:
            return self.description

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

    def reprice(self, new_price: Price, multiplier: Decimal = Decimal(1), round_to_99_cents: bool = False,
                max_change: Decimal | None = MAX_PRICE_CHANGE, show_out_of_stock: bool = False,
                min_change: Decimal = MIN_PRICE_CHANGE_TO_SKIP):
        if not new_price:
            return

        if round_to_99_cents:
            new_price = Price(round_up_to_99_cents(new_price.price * multiplier))
        else:
            new_price = Price(new_price.price * multiplier)

        if new_price == self.marketplace_price:
            return

        percent_change = self.percent_change_to(new_price)
        if self.marketplace_price:
            previous_price = f'${self.marketplace_price}'
        else:
            previous_price = 'no price'

        absolute_change = abs(new_price.or_zero() - self.marketplace_price.or_zero())
        if max_change is not None and percent_change is not None \
                and abs(percent_change) > max_change and absolute_change >= min_change:
            if self.total_quantity > 0 or show_out_of_stock:
                print(f'Not repricing {self.description} from {previous_price} to ${new_price}: a '
                      f'{percent_change.quantize(Decimal("0.1"))}% difference is over the {max_change:.0f}% limit. '
                      f'Reprice it by hand if that is correct.')
            return

        # Products you do not hold are repriced too, so their price is current when
        # you restock, but they are not worth reporting unless asked for.
        if self.total_quantity > 0 or show_out_of_stock:
            if percent_change is None:
                difference = ''
            else:
                difference = f' (a {percent_change.quantize(Decimal("0.1"))}% difference)'
            print(f'Repricing {self.description} from {previous_price} to ${new_price}{difference}')
        self.marketplace_price = new_price


def get_total_price(products: list[Product]) -> Decimal:
    total = sum((product.marketplace_price.or_zero() * product.total_quantity for product in products), Decimal(0))
    return total.quantize(Decimal('0.01'))
