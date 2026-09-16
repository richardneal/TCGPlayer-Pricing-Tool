#!/usr/bin/env python3
# Copyright (c) 2022, Richard Neal
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

import sys

from CLI import base_parser, parse_arguments
from CSV import CSVError, input_csv
from Product import get_total_price


def main():
    arguments = parse_arguments(base_parser('List the products in a TCGPlayer pricing export by price.'))
    products_list = input_csv(arguments.csv_file)

    print(f'Total price: ${get_total_price(products_list)}')
    for product in sorted(products_list, key=lambda product: product.marketplace_price, reverse=True):
        if product.total_quantity:
            print(product)


if __name__ == '__main__':
    try:
        main()
    except CSVError as error:
        sys.exit(f'Error: {error}')
