# Copyright (c) 2022, Richard Neal
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.
from __future__ import annotations

import argparse
from decimal import Decimal, InvalidOperation
from os.path import exists
from pathlib import Path

DEFAULT_FILENAME = 'TCG.csv'

# Where TCGPlayer exports land, and what they are called, for --latest.
DOWNLOADS_DIRECTORY = Path.home() / 'Downloads'
EXPORT_PATTERN = 'TCGplayer*MyPricing*.csv'

# What repriced CSVs are named with. --latest has to skip them, or repricing an
# export twice would compound its own markup.
OUTPUT_SUFFIX = '_OUTPUT'


def decimal_argument(value: str) -> Decimal:
    try:
        return Decimal(value)
    except InvalidOperation:
        raise argparse.ArgumentTypeError(f'{value!r} is not a number')


def latest_export(directory: Path = DOWNLOADS_DIRECTORY, pattern: str = EXPORT_PATTERN) -> Path | None:
    """The most recently downloaded TCGPlayer export, or None if there are none.

    Output CSVs this tool wrote are skipped, so that repricing --latest twice does
    not reprice its own output.
    """
    candidates = [export for export in directory.glob(pattern) if not export.stem.endswith(OUTPUT_SUFFIX)]
    exports = sorted(candidates, key=lambda export: export.stat().st_mtime, reverse=True)
    if exports:
        return exports[0]
    else:
        return None


def base_parser(description: str) -> argparse.ArgumentParser:
    """A parser taking the pricing export to read, for a script to add its own options to."""
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('csv_file', nargs='?',
                        help=f'TCGPlayer pricing export to read (default: {DEFAULT_FILENAME})')
    parser.add_argument('--latest', action='store_true',
                        help=f'read the most recent {EXPORT_PATTERN} in {DOWNLOADS_DIRECTORY} instead')
    return parser


def parse_arguments(parser: argparse.ArgumentParser) -> argparse.Namespace:
    arguments = parser.parse_args()

    if arguments.latest:
        if arguments.csv_file is not None:
            parser.error('pass either a file or --latest, not both')
        export = latest_export()
        if export is None:
            parser.error(f'no export matching {EXPORT_PATTERN} in {DOWNLOADS_DIRECTORY}')
        arguments.csv_file = str(export)
        # Always say which file was picked, since nobody typed it.
        print(f'Reading {arguments.csv_file}')
    elif arguments.csv_file is None:
        arguments.csv_file = DEFAULT_FILENAME

    if not exists(arguments.csv_file):
        parser.error(f'no such file: {arguments.csv_file}')
    return arguments
