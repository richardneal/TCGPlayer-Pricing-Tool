# Copyright (c) 2022, Richard Neal
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

import argparse
from os.path import exists

DEFAULT_FILENAME = 'TCG.csv'


def input_filename(description: str) -> str:
    """The pricing export to read, from argv, failing loudly if it is not there."""
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('csv_file', nargs='?', default=DEFAULT_FILENAME,
                        help=f'TCGPlayer pricing export to read (default: {DEFAULT_FILENAME})')
    arguments = parser.parse_args()

    if not exists(arguments.csv_file):
        parser.error(f'no such file: {arguments.csv_file}')
    return arguments.csv_file
