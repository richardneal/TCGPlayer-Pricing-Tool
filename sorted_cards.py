# Copyright (c) 2022, Richard Neal
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

import sys
from os.path import exists

from CSV import input_csv
from Product import Product


def get_total_price(products: list[Product]) -> float:
    return round(sum((product.marketplace_price.price * product.total_quantity for product in products)), 2)


def main():
    arguments = sys.argv[1:]
    input_filename = 'TCG.csv'
    if arguments:
        filename_argument = arguments[0]
        if exists(filename_argument):
            input_filename = filename_argument
        elif not exists(input_filename):
            raise Exception('Either no filename was input, or it was invalid.')

    products_list = input_csv(input_filename)

    print(f'Total price: ${get_total_price(products_list)}')
    for product in sorted(products_list, key=lambda product: product.marketplace_price, reverse=True):
        if product.total_quantity:
            print(product)


if __name__ == '__main__':
    main()

