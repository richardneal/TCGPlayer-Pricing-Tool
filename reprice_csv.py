# Copyright (c) 2022, Richard Neal
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

import csv
import os.path
import sys
from os.path import exists

from Enums.Headers import Headers
from Product import Product


def input_csv(filename: str) -> list[Product]:
    products = []
    with open(filename, 'r') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            param_dict = {header.name.lower(): row[header.value] for header in Headers}
            products.append(Product(**param_dict))
    return products


def output_csv(filename: str, products: list[Product]):
    with open(filename, 'w') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow((header.value for header in Headers))
        for product in products:
            writer.writerow(product.to_row())


def price_products(products: list[Product]):
    for product in products:
        # If the product has a Direct Low price, or is sealed, set it to the highest of Direct Low or TCGLow + Shipping
        if product.direct_low_price or product.condition.is_sealed():
            new_price = max(product.direct_low_price, product.low_price_with_shipping)
            product.reprice(new_price)
        # Otherwise, set it to 1.1x TCGLow + Shipping, rounded to 99 cents
        elif product.low_price_with_shipping:
            product.reprice(product.low_price_with_shipping, 1.1, True)


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

    print(f'Total price before repricing: ${get_total_price(products_list)}')
    price_products(products_list)
    print(f'Total price after repricing: ${get_total_price(products_list)}')

    split_output_filename = os.path.splitext(input_filename)
    output_filename = f'{split_output_filename[0]}_OUTPUT{split_output_filename[1]}'

    print(f'Writing to {output_filename}')
    output_csv(output_filename, products_list)


if __name__ == '__main__':
    main()