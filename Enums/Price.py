# Copyright (c) 2022, Richard Neal
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

import functools
from decimal import Decimal, InvalidOperation, ROUND_CEILING, ROUND_HALF_UP

# Prices are held as Decimal rather than float: the repricing rules multiply and
# round, and float error there is worth real money.
CENT = Decimal('0.01')

# Anything below a cent is not a price TCGPlayer will accept, so treat it as unset.
PRICE_FLOOR = CENT

# What an unpriced product is listed at, so that it is obvious and easy to find
# in the output CSV rather than being quietly sold at a placeholder price.
SYP_DEFAULT_PRICE = Decimal('999.99')


def round_up_to_99_cents(amount: Decimal) -> Decimal:
    return amount.to_integral_value(rounding=ROUND_CEILING) - CENT


@functools.total_ordering
class Price:
    """A single price. An unset price (a blank cell in the CSV) is distinct from $0.00."""

    price: Decimal | None

    def __init__(self, price: str | float | Decimal | None = None):
        self.price = self._parse(price)

    @staticmethod
    def _parse(price: str | float | Decimal | None) -> Decimal | None:
        if price is None or price == '':
            return None

        try:
            amount = Decimal(str(price).strip())
        except InvalidOperation:
            return None

        if not amount.is_finite() or amount < PRICE_FLOOR:
            return None

        return amount.quantize(CENT, rounding=ROUND_HALF_UP)

    def or_zero(self) -> Decimal:
        """The price as a Decimal, treating an unset price as zero, for totalling."""
        return self.price if self.price is not None else Decimal(0)

    def __eq__(self, other):
        if not isinstance(other, Price):
            return NotImplemented
        return self.price == other.price

    def __lt__(self, other):
        # An unset price sorts below every real price, so max() prefers a real one.
        if not isinstance(other, Price):
            return NotImplemented
        return self.or_zero() < other.or_zero()

    def __hash__(self):
        return hash(self.price)

    def __str__(self):
        if not self:
            return 'No price set'
        else:
            return f'{self.price:.2f}'

    def to_csv(self) -> str:
        if not self:
            return ''
        else:
            return f'{self.price:.2f}'

    def __bool__(self):
        return self.price is not None
