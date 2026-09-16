# Copyright (c) 2022, Richard Neal
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

import csv

from Enums.Headers import Headers
from Product import Product


class CSVError(Exception):
    """A CSV that is not the TCGPlayer pricing export this tool expects."""


def input_csv(filename: str) -> list[Product]:
    products = []
    with open(filename, 'r', newline='') as csv_file:
        reader = csv.DictReader(csv_file)

        missing = [header.value for header in Headers if header.value not in (reader.fieldnames or [])]
        if missing:
            raise CSVError(f'{filename} is missing the column(s): {", ".join(missing)}. '
                           f'It should be a pricing export from TCGPlayer.')

        for row in reader:
            param_dict = {header.name.lower(): row[header.value] for header in Headers}
            try:
                products.append(Product(**param_dict))
            except (ValueError, TypeError) as error:
                raise CSVError(f'{filename} line {reader.line_num}: {error}') from error
    return products


def output_csv(filename: str, products: list[Product]):
    with open(filename, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow((header.value for header in Headers))
        for product in products:
            writer.writerow(product.to_row())
