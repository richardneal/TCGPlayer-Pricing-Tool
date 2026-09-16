# Copyright (c) 2022, Richard Neal
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

import unittest
from decimal import Decimal

from Enums.Price import Price, SYP_DEFAULT_PRICE
from reprice_csv import price_products
from tests.support import captured_output, make_product


class PricingRulesTest(unittest.TestCase):
    def priced(self, **overrides) -> Price:
        product = make_product(**overrides)
        captured_output(price_products, [product])
        return product.marketplace_price

    def test_a_product_with_a_direct_low_takes_the_higher_comparable(self):
        self.assertEqual(self.priced(direct_low_price='60.00', low_price_with_shipping='50.00'), Price('60.00'))
        self.assertEqual(self.priced(direct_low_price='40.00', low_price_with_shipping='50.00'), Price('50.00'))

    def test_a_sealed_product_takes_the_higher_comparable_without_a_direct_low(self):
        self.assertEqual(self.priced(condition='Unopened', rarity='', direct_low_price='',
                                     low_price_with_shipping='50.00'), Price('50.00'))

    def test_anything_else_is_marked_up_and_rounded_to_99_cents(self):
        self.assertEqual(self.priced(direct_low_price='', low_price_with_shipping='50.00'), Price('54.99'))

    def test_a_product_with_nothing_to_compare_against_keeps_its_price(self):
        # The README used to claim these were set to the placeholder price.
        self.assertEqual(self.priced(direct_low_price='', low_price_with_shipping='',
                                     marketplace_price='5.00'), Price('5.00'))

    def test_an_unpriced_product_with_nothing_to_compare_against_gets_the_placeholder(self):
        product = make_product(direct_low_price='', low_price_with_shipping='', marketplace_price='')
        output = captured_output(price_products, [product])
        self.assertEqual(product.marketplace_price, Price(SYP_DEFAULT_PRICE))
        self.assertIn('has no price and nothing to compare it against', output)

    def test_the_markup_is_configurable(self):
        product = make_product(direct_low_price='', low_price_with_shipping='50.00')
        captured_output(price_products, [product], Decimal('1.25'))
        self.assertEqual(product.marketplace_price, Price('62.99'))


class IdempotenceTest(unittest.TestCase):
    def test_pricing_twice_changes_nothing_the_second_time(self):
        # Reprice targets come from the TCGPlayer columns, which are carried through
        # unchanged, so a second pass over an already priced export is a no-op. If
        # this ever stops holding, repricing an output CSV would drift.
        products = [make_product(direct_low_price='', low_price_with_shipping='50.00'),
                    make_product(direct_low_price='60.00', low_price_with_shipping='50.00'),
                    make_product(condition='Unopened', rarity='', low_price_with_shipping='20.00')]
        captured_output(price_products, products)
        after_one_pass = [product.marketplace_price for product in products]

        second_pass_output = captured_output(price_products, products)
        self.assertEqual([product.marketplace_price for product in products], after_one_pass)
        self.assertEqual(second_pass_output, '')


if __name__ == '__main__':
    unittest.main()
