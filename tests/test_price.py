# Copyright (c) 2022, Richard Neal
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

import unittest
from decimal import Decimal

from Enums.Price import PRICE_FLOOR, Price, SYP_DEFAULT_PRICE, round_up_to_99_cents


class RoundUpTo99CentsTest(unittest.TestCase):
    def test_marks_up_to_the_next_99_cents(self):
        # The pairs that land on an exact integer are the ones that used to depend
        # on float representation: 50.00 * 1.1 is 55.00000000000001 as a float, so
        # it rounded up to 55.99 while 20.00 * 1.1 gave exactly 22.0 and 21.99.
        for base, expected in [(Decimal('50.00'), Decimal('54.99')),
                               (Decimal('20.00'), Decimal('21.99')),
                               (Decimal('10.00'), Decimal('10.99')),
                               (Decimal('30.00'), Decimal('32.99')),
                               (Decimal('1300.00'), Decimal('1429.99')),
                               (Decimal('1200.00'), Decimal('1319.99')),
                               (Decimal('45.00'), Decimal('49.99')),
                               (Decimal('4.99'), Decimal('5.99'))]:
            with self.subTest(base=base):
                self.assertEqual(round_up_to_99_cents(base * Decimal('1.1')), expected)

    def test_is_stable_on_a_price_already_at_99_cents(self):
        self.assertEqual(round_up_to_99_cents(Decimal('54.99')), Decimal('54.99'))


class DecimalArithmeticTest(unittest.TestCase):
    def test_amounts_are_decimal_not_float(self):
        # The markup is computed as price * multiplier and then rounded up. Doing
        # that in float is what made $50.00 come out at $55.99 instead of $54.99,
        # because 50.0 * 1.1 is 55.00000000000001, while $20.00 was unaffected.
        self.assertIsInstance(Price('50.00').price, Decimal)

    def test_marking_up_a_price_that_lands_on_a_whole_number_is_exact(self):
        for base in ('50.00', '20.00', '10.00', '30.00', '1300.00', '1200.00'):
            with self.subTest(base=base):
                marked_up = Price(base).price * Decimal('1.1')
                self.assertEqual(marked_up, marked_up.to_integral_value(),
                                 f'{base} x 1.1 should be exact, not {marked_up}')


class PriceParsingTest(unittest.TestCase):
    def test_parses_the_four_decimal_places_tcgplayer_exports(self):
        self.assertEqual(Price('10.9900').price, Decimal('10.99'))

    def test_an_empty_cell_is_unset_rather_than_zero(self):
        for empty in ('', None):
            with self.subTest(empty=empty):
                price = Price(empty)
                self.assertIsNone(price.price)
                self.assertFalse(price)

    def test_below_a_cent_is_unset(self):
        self.assertFalse(Price('0.005'))
        self.assertTrue(Price(PRICE_FLOOR))

    def test_the_placeholder_price_is_still_a_real_price(self):
        # $999.99 used to double as the "no price" sentinel, so a card genuinely
        # worth that much read as unpriced.
        price = Price(SYP_DEFAULT_PRICE)
        self.assertTrue(price)
        self.assertEqual(price.price, Decimal('999.99'))

    def test_nonsense_is_unset_rather_than_an_exception(self):
        self.assertFalse(Price('not a number'))


class PriceRenderingTest(unittest.TestCase):
    def test_renders_two_decimal_places(self):
        self.assertEqual(str(Price('105')), '105.00')
        self.assertEqual(Price('105').to_csv(), '105.00')

    def test_an_unset_price_reads_as_unset_and_writes_as_blank(self):
        self.assertEqual(str(Price('')), 'No price set')
        self.assertEqual(Price('').to_csv(), '')


class PriceComparisonTest(unittest.TestCase):
    def test_orders_by_amount(self):
        self.assertLess(Price('1.00'), Price('2.00'))
        self.assertGreater(Price('2.00'), Price('1.00'))
        self.assertGreaterEqual(Price('2.00'), Price('2.00'))
        self.assertEqual(Price('2.00'), Price('2.0000'))

    def test_an_unset_price_sorts_below_a_real_one(self):
        self.assertLess(Price(''), Price('0.01'))
        self.assertEqual(max(Price(''), Price('5.00')), Price('5.00'))

    def test_is_not_equal_to_things_that_are_not_prices(self):
        self.assertNotEqual(Price('5.00'), 5.0)

    def test_is_hashable(self):
        self.assertEqual(len({Price('5.00'), Price('5.00'), Price('6.00')}), 2)


if __name__ == '__main__':
    unittest.main()
