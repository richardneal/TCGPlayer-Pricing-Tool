# Copyright (c) 2022, Richard Neal
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

import contextlib
import io

from Enums.Headers import Headers
from Product import Product

# A plausible row, by the keyword names Product takes, for tests to vary one
# field of at a time.
DEFAULT_ROW = {
    'tcgplayer_id': '12345',
    'product_line': 'Magic',
    'set_name': 'Alpha',
    'product_name': 'Black Lotus',
    'title': '',
    'number': '233',
    'rarity': 'R',
    'condition': 'Near Mint',
    'market_price': '100.00',
    'direct_low_price': '',
    'low_price_with_shipping': '50.00',
    'low_price': '45.00',
    'total_quantity': '2',
    'add_to_quantity': '0',
    'marketplace_price': '105.00',
    'photo_url': '',
}


def make_product(**overrides) -> Product:
    return Product(**{**DEFAULT_ROW, **overrides})


def csv_text(*rows: dict) -> str:
    """A CSV export with the real header row and one line per given row."""
    header = ','.join(header.value for header in Headers)
    lines = [header]
    for row in rows:
        values = {**DEFAULT_ROW, **row}
        lines.append(','.join(values[header.name.lower()] for header in Headers))
    return '\n'.join(lines) + '\n'


def captured_output(function, *args, **kwargs) -> str:
    """Run function and return what it printed."""
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        function(*args, **kwargs)
    return output.getvalue()
