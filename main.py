# Copyright (c) 2022, Richard Neal
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

import csv

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
        # If the product has a Direct Low price, set it to the highest of that or TCGLow + Shipping
        if product.direct_low_price:
            new_price = max(product.direct_low_price, product.low_price_with_shipping)
            product.reprice(new_price)
        # Otherwise, set it to 1.1x TCGLow + Shipping, rounded to 99 cents
        elif product.low_price_with_shipping:
            product.reprice(product.low_price_with_shipping, 1.1, True)


def get_total_price(products: list[Product]) -> float:
    return round(sum((product.marketplace_price.price * product.total_quantity for product in products)), 2)


if __name__ == '__main__':
    products_list = input_csv('TCG.csv')

    print(f'Total price before repricing: ${get_total_price(products_list)}')
    price_products(products_list)
    print(f'Total price after repricing: ${get_total_price(products_list)}')

    output_csv('TCG_OUTPUT.csv', products_list)
