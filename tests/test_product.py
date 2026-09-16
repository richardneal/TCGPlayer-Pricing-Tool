# Copyright (c) 2022, Richard Neal
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

import unittest
from decimal import Decimal

from Enums.Headers import Headers
from Enums.Price import Price, SYP_DEFAULT_PRICE
from Product import get_total_price
from tests.support import captured_output, make_product


class ProductParsingTest(unittest.TestCase):
    def test_sealed_products_are_product_rarity_whatever_the_column_says(self):
        self.assertEqual(make_product(condition='Unopened', rarity='').rarity.value, '')

    def test_an_unrecognised_rarity_says_so(self):
        with self.assertRaises(ValueError) as raised:
            make_product(rarity='X')
        self.assertIn('X', str(raised.exception))


class ProductDescriptionTest(unittest.TestCase):
    def test_describes_the_product_without_its_price(self):
        product = make_product(total_quantity='2', condition='Near Mint Foil')
        self.assertEqual(product.description, '2x Alpha: Black Lotus - Near Mint Foil')

    def test_a_non_foil_does_not_leave_a_double_space(self):
        self.assertEqual(make_product().description, '2x Alpha: Black Lotus - Near Mint')

    def test_str_appends_the_price_when_there_is_one(self):
        self.assertEqual(str(make_product()), '2x Alpha: Black Lotus - Near Mint - $105.00')

    def test_str_says_nothing_about_price_when_there_is_none(self):
        self.assertEqual(str(make_product(marketplace_price='')), '2x Alpha: Black Lotus - Near Mint')


class ToRowTest(unittest.TestCase):
    def row(self, **overrides) -> dict:
        product = make_product(**overrides)
        return dict(zip((header.value for header in Headers), product.to_row()))

    def test_writes_one_value_per_header_in_header_order(self):
        self.assertEqual(len(make_product().to_row()), len(list(Headers)))

    def test_writes_prices_to_two_decimal_places(self):
        self.assertEqual(self.row(marketplace_price='120')['TCG Marketplace Price'], '120.00')

    def test_leaves_blank_price_cells_blank(self):
        # These used to come back as "0.0", turning "no data" into a real zero.
        self.assertEqual(self.row(direct_low_price='')['TCG Direct Low'], '')

    def test_an_unpriced_product_gets_the_placeholder_not_an_enum(self):
        # The enum member was written instead of its value, so this column read
        # "Consts.SYP_DEFAULT_PRICE" in the CSV TCGPlayer imports.
        self.assertEqual(self.row(marketplace_price='')['TCG Marketplace Price'], f'{SYP_DEFAULT_PRICE:.2f}')

    def test_round_trips_the_condition_string_it_was_given(self):
        self.assertEqual(self.row(condition='Near Mint Foil - Chinese (S)')['Condition'],
                         'Near Mint Foil - Chinese (S)')


class RepriceTest(unittest.TestCase):
    def test_applies_a_new_price(self):
        product = make_product(marketplace_price='105.00')
        captured_output(product.reprice, Price('120.00'))
        self.assertEqual(product.marketplace_price, Price('120.00'))

    def test_marks_up_and_rounds_to_99_cents(self):
        product = make_product(marketplace_price='40.00')
        captured_output(product.reprice, Price('50.00'), Decimal('1.1'), True)
        self.assertEqual(product.marketplace_price, Price('54.99'))

    def test_ignores_an_unset_new_price(self):
        product = make_product(marketplace_price='105.00')
        captured_output(product.reprice, Price(''))
        self.assertEqual(product.marketplace_price, Price('105.00'))

    def test_repricing_to_the_same_price_says_nothing(self):
        product = make_product(marketplace_price='105.00')
        self.assertEqual(captured_output(product.reprice, Price('105.00')), '')

    def test_reports_the_price_it_moved_from_and_to(self):
        product = make_product(marketplace_price='105.00')
        output = captured_output(product.reprice, Price('120.00'))
        self.assertIn('from $105.00 to $120.00', output)
        self.assertIn('14.3% difference', output)

    def test_reports_having_had_no_previous_price(self):
        product = make_product(marketplace_price='')
        self.assertIn('from no price to $6.99', captured_output(product.reprice, Price('6.99')))


class RepriceLimitTest(unittest.TestCase):
    def test_applies_every_reprice_by_default(self):
        product = make_product(marketplace_price='10.00')
        captured_output(product.reprice, Price('100.00'))
        self.assertEqual(product.marketplace_price, Price('100.00'))

    def test_holds_back_a_change_over_the_limit(self):
        product = make_product(marketplace_price='10.00')
        output = captured_output(product.reprice, Price('100.00'), max_change=Decimal('50'))
        self.assertEqual(product.marketplace_price, Price('10.00'))
        self.assertIn('Not repricing', output)

    def test_a_large_percentage_of_very_little_is_not_worth_holding_back(self):
        # $1.98 to $2.99 is 51%, and a dollar.
        product = make_product(marketplace_price='1.98')
        captured_output(product.reprice, Price('2.99'), max_change=Decimal('50'))
        self.assertEqual(product.marketplace_price, Price('2.99'))

    def test_min_change_zero_holds_back_the_small_ones_too(self):
        product = make_product(marketplace_price='1.98')
        captured_output(product.reprice, Price('2.99'), max_change=Decimal('50'), min_change=Decimal(0))
        self.assertEqual(product.marketplace_price, Price('1.98'))


class OutOfStockReportingTest(unittest.TestCase):
    def test_still_reprices_what_you_do_not_hold(self):
        product = make_product(total_quantity='0', marketplace_price='105.00')
        captured_output(product.reprice, Price('120.00'))
        self.assertEqual(product.marketplace_price, Price('120.00'))

    def test_says_nothing_about_it_by_default(self):
        product = make_product(total_quantity='0', marketplace_price='105.00')
        self.assertEqual(captured_output(product.reprice, Price('120.00')), '')

    def test_reports_it_when_asked(self):
        product = make_product(total_quantity='0', marketplace_price='105.00')
        output = captured_output(product.reprice, Price('120.00'), show_out_of_stock=True)
        self.assertIn('from $105.00 to $120.00', output)

    def test_holding_one_back_is_quiet_too(self):
        product = make_product(total_quantity='0', marketplace_price='10.00')
        self.assertEqual(captured_output(product.reprice, Price('100.00'), max_change=Decimal('50')), '')


class TotalPriceTest(unittest.TestCase):
    def test_totals_price_times_quantity(self):
        products = [make_product(marketplace_price='10.00', total_quantity='2'),
                    make_product(marketplace_price='1.25', total_quantity='4')]
        self.assertEqual(get_total_price(products), Decimal('25.00'))

    def test_an_unpriced_product_counts_as_nothing(self):
        self.assertEqual(get_total_price([make_product(marketplace_price='', total_quantity='3')]), Decimal('0.00'))


if __name__ == '__main__':
    unittest.main()
