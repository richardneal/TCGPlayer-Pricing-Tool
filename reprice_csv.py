#!/usr/bin/env python3
# Copyright (c) 2022, Richard Neal
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

import os.path
import sys
from decimal import Decimal

from CLI import OUTPUT_SUFFIX, base_parser, decimal_argument, parse_arguments
from CSV import CSVError, output_csv, input_csv
from Enums.Price import Price, SYP_DEFAULT_PRICE
from Product import MAX_PRICE_CHANGE, MIN_PRICE_CHANGE_TO_SKIP, Product, get_total_price

# What to mark a product up by when pricing off TCG Low + Shipping.
MARKUP = Decimal('1.1')


def price_products(products: list[Product], markup: Decimal = MARKUP,
                   max_change: Decimal | None = MAX_PRICE_CHANGE, show_out_of_stock: bool = False,
                   min_change: Decimal = MIN_PRICE_CHANGE_TO_SKIP):
    for product in products:
        # If the product has a Direct Low price, or is sealed, set it to the highest of Direct Low or TCGLow + Shipping
        if product.direct_low_price or product.condition.is_sealed():
            new_price = max(product.direct_low_price, product.low_price_with_shipping)
            product.reprice(new_price, max_change=max_change, show_out_of_stock=show_out_of_stock,
                            min_change=min_change)
        # Otherwise, set it to 1.1x TCGLow + Shipping, rounded to 99 cents
        elif product.low_price_with_shipping:
            product.reprice(product.low_price_with_shipping, markup, True, max_change=max_change,
                            show_out_of_stock=show_out_of_stock, min_change=min_change)

        # Anything still unpriced has no comparable products to price against, so
        # flag it rather than listing it at whatever TCGPlayer happens to default to.
        if not product.marketplace_price:
            print(f'{product} has no price and nothing to compare it against. Defaulting it to '
                  f'${SYP_DEFAULT_PRICE}, which you should change in the output CSV')
            product.marketplace_price = Price(SYP_DEFAULT_PRICE)


def default_output_filename(input_filename: str) -> str:
    root, extension = os.path.splitext(input_filename)
    return f'{root}{OUTPUT_SUFFIX}{extension}'


def main():
    parser = base_parser('Reprice a TCGPlayer pricing export.')
    parser.add_argument('-o', '--output', metavar='CSV_FILE',
                        help='where to write the repriced CSV (default: <input>_OUTPUT.csv)')
    parser.add_argument('--show-out-of-stock', action='store_true',
                        help='also report reprices of products you have none of')
    parser.add_argument('--markup', type=decimal_argument, default=MARKUP,
                        help=f'what to multiply TCG Low + Shipping by (default: {MARKUP})')
    parser.add_argument('--max-change', type=decimal_argument, default=MAX_PRICE_CHANGE, metavar='PERCENT',
                        help='report and skip reprices that move a price by more than this percent '
                             '(default: no limit, every reprice is applied)')
    parser.add_argument('--min-change', type=decimal_argument, default=MIN_PRICE_CHANGE_TO_SKIP,
                        metavar='DOLLARS',
                        help=f'only apply --max-change to changes of at least this many dollars '
                             f'(default: {MIN_PRICE_CHANGE_TO_SKIP})')
    arguments = parse_arguments(parser)

    products_list = input_csv(arguments.csv_file)

    print(f'Total price before repricing: ${get_total_price(products_list)}')
    price_products(products_list, arguments.markup, arguments.max_change, arguments.show_out_of_stock,
                   arguments.min_change)
    print(f'Total price after repricing: ${get_total_price(products_list)}')

    output_filename = arguments.output or default_output_filename(arguments.csv_file)
    print(f'Writing to {output_filename}')
    output_csv(output_filename, products_list)


if __name__ == '__main__':
    try:
        main()
    except CSVError as error:
        sys.exit(f'Error: {error}')
