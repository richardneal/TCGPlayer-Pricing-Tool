# Copyright (c) 2022, Richard Neal
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

import os
import tempfile
import unittest
from pathlib import Path

from CLI import OUTPUT_SUFFIX, latest_export
from reprice_csv import default_output_filename


class DefaultOutputFilenameTest(unittest.TestCase):
    def test_appends_the_suffix_before_the_extension(self):
        self.assertEqual(default_output_filename('TCG.csv'), f'TCG{OUTPUT_SUFFIX}.csv')
        self.assertEqual(default_output_filename('/tmp/a/b.csv'), f'/tmp/a/b{OUTPUT_SUFFIX}.csv')


class LatestExportTest(unittest.TestCase):
    def setUp(self):
        self.directory = Path(tempfile.mkdtemp())

    def touch(self, name: str, age_in_seconds: int = 0) -> Path:
        path = self.directory / name
        path.write_text('')
        os.utime(path, (0, 1_000_000 - age_in_seconds))
        return path

    def test_finds_nothing_in_an_empty_directory(self):
        self.assertIsNone(latest_export(self.directory))

    def test_picks_the_most_recent_export(self):
        self.touch('TCGplayer__MyPricing_20260101_000000.csv', age_in_seconds=100)
        newest = self.touch('TCGplayer__MyPricing_20260916_020622.csv')
        self.assertEqual(latest_export(self.directory), newest)

    def test_ignores_files_that_are_not_exports(self):
        self.touch('something-else.csv')
        self.assertIsNone(latest_export(self.directory))

    def test_ignores_its_own_output(self):
        # The export glob also matched the _OUTPUT.csv written beside an input, so
        # repricing --latest twice read back its own output: the prices come out the
        # same, but you would be working from a derived file rather than whatever
        # TCGPlayer's market data says now.
        export = self.touch('TCGplayer__MyPricing_20260916_020622.csv', age_in_seconds=100)
        self.touch(f'TCGplayer__MyPricing_20260916_020622{OUTPUT_SUFFIX}.csv')
        self.assertEqual(latest_export(self.directory), export)


if __name__ == '__main__':
    unittest.main()
