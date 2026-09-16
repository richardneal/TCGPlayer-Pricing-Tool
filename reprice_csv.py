# Copyright (c) 2022, Richard Neal
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

import os.path
import sys
from decimal import Decimal

from CLI import input_filename
from CSV import CSVError, output_csv, input_csv
from Enums.Price import Price, SYP_DEFAULT_PRICE
from Product import Product, get_total_price

# What to mark a product up by when pricing off TCG Low + Shipping.
MARKUP = Decimal('1.1')


def price_products(products: list[Product]):
    for product in products:
        # If the product has a Direct Low price, or is sealed, set it to the highest of Direct Low or TCGLow + Shipping
        if product.direct_low_price or product.condition.is_sealed():
            new_price = max(product.direct_low_price, product.low_price_with_shipping)
            product.reprice(new_price)
        # Otherwise, set it to 1.1x TCGLow + Shipping, rounded to 99 cents
        elif product.low_price_with_shipping:
            product.reprice(product.low_price_with_shipping, MARKUP, True)

        # Anything still unpriced has no comparable products to price against, so
        # flag it rather than listing it at whatever TCGPlayer happens to default to.
        if not product.marketplace_price:
            print(f'{product} has no price and nothing to compare it against. Defaulting it to '
                  f'${SYP_DEFAULT_PRICE}, which you should change in the output CSV')
            product.marketplace_price = Price(SYP_DEFAULT_PRICE)


def main():
    input_csv_filename = input_filename('Reprice a TCGPlayer pricing export.')
    products_list = input_csv(input_csv_filename)

    print(f'Total price before repricing: ${get_total_price(products_list)}')
    price_products(products_list)
    print(f'Total price after repricing: ${get_total_price(products_list)}')

    split_output_filename = os.path.splitext(input_csv_filename)
    output_filename = f'{split_output_filename[0]}_OUTPUT{split_output_filename[1]}'

    print(f'Writing to {output_filename}')
    output_csv(output_filename, products_list)


if __name__ == '__main__':
    try:
        main()
    except CSVError as error:
        sys.exit(f'Error: {error}')
