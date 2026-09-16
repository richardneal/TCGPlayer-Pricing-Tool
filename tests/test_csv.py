# Copyright (c) 2022, Richard Neal
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

import csv
import tempfile
import unittest
from pathlib import Path

from CSV import CSVError, input_csv, output_csv
from tests.support import csv_text


class CSVTestCase(unittest.TestCase):
    def setUp(self):
        self.directory = Path(tempfile.mkdtemp())

    def written(self, name: str, text: str) -> str:
        path = self.directory / name
        path.write_text(text)
        return str(path)

    def round_tripped(self, *rows: dict) -> list[dict]:
        """Read an export, write it straight back out, and return the written rows."""
        products = input_csv(self.written('in.csv', csv_text(*rows)))
        output_filename = str(self.directory / 'out.csv')
        output_csv(output_filename, products)
        with open(output_filename, newline='') as written:
            return list(csv.DictReader(written))


class InputCSVTest(CSVTestCase):
    def test_reads_every_row(self):
        products = input_csv(self.written('in.csv', csv_text({}, {'tcgplayer_id': '2'})))
        self.assertEqual([product.tcgplayer_id for product in products], ['12345', '2'])

    def test_a_csv_that_is_not_an_export_names_the_missing_columns(self):
        with self.assertRaises(CSVError) as raised:
            input_csv(self.written('wrong.csv', 'a,b\n1,2\n'))
        self.assertIn('TCGplayer Id', str(raised.exception))

    def test_a_bad_row_names_the_line_it_is_on(self):
        # The underlying ValueError used to surface with no clue which row caused it.
        with self.assertRaises(CSVError) as raised:
            input_csv(self.written('in.csv', csv_text({}, {'condition': 'Mint-ish'})))
        self.assertIn('line 3', str(raised.exception))
        self.assertIn('Mint-ish', str(raised.exception))


class RoundTripTest(CSVTestCase):
    def test_keeps_the_columns_it_was_given(self):
        [row] = self.round_tripped({'condition': 'Near Mint Foil - Chinese (S)'})
        self.assertEqual(row['TCGplayer Id'], '12345')
        self.assertEqual(row['Set Name'], 'Alpha')
        self.assertEqual(row['Condition'], 'Near Mint Foil - Chinese (S)')
        self.assertEqual(row['Total Quantity'], '2')

    def test_keeps_blank_price_cells_blank(self):
        [row] = self.round_tripped({'direct_low_price': '', 'low_price': ''})
        self.assertEqual(row['TCG Direct Low'], '')
        self.assertEqual(row['TCG Low Price'], '')

    def test_keeps_prices_equal_while_normalising_them_to_two_places(self):
        [row] = self.round_tripped({'low_price_with_shipping': '10.9900'})
        self.assertEqual(row['TCG Low Price With Shipping'], '10.99')

    def test_keeps_the_rows_in_order(self):
        rows = self.round_tripped({'tcgplayer_id': '1'}, {'tcgplayer_id': '2'}, {'tcgplayer_id': '3'})
        self.assertEqual([row['TCGplayer Id'] for row in rows], ['1', '2', '3'])


if __name__ == '__main__':
    unittest.main()
