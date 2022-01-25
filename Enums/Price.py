# Copyright (c) 2022, Richard Neal
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

from enum import Enum


class Consts(Enum):
    PRICE_FLOOR = 0.01
    SYP_DEFAULT_PRICE = 999.99


class Price:
    price: float

    def __init__(self, price: str | float):
        if price:
            price = float(price)
        else:
            price = 0.0

        if price < Consts.PRICE_FLOOR.value or price == Consts.SYP_DEFAULT_PRICE.value:
            self.price = 0.0
        else:
            self.price = float(price)

    def __eq__(self, other):
        if isinstance(other, Price):
            return self.price == other.price
        else:
            return False

    def __lt__(self, other):
        if isinstance(other, Price):
            return self.price < other.price
        else:
            return False

    def __str__(self):
        if not self:
            return 'No price set'
        else:
            return f'{round(self.price, 2)}'

    def __bool__(self):
        return self.price != 0.0
