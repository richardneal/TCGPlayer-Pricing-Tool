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
