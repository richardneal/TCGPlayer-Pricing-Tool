# Copyright (c) 2022, Richard Neal
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

import unittest

from Enums.Condition import Condition, Conditions, Finishes, Languages


class ConditionParsingTest(unittest.TestCase):
    def test_reads_the_condition(self):
        for string, expected in [('Near Mint', Conditions.NEAR_MINT),
                                 ('Lightly Played', Conditions.LIGHTLY_PLAYED),
                                 ('Moderately Played', Conditions.MODERATELY_PLAYED),
                                 ('Heavily Played', Conditions.HEAVILY_PLAYED),
                                 ('Damaged', Conditions.DAMAGED),
                                 ('Unopened', Conditions.UNOPENED)]:
            with self.subTest(string=string):
                self.assertIs(Condition(string).condition, expected)

    def test_reads_the_finish(self):
        self.assertIs(Condition('Near Mint Foil').finish, Finishes.FOIL)
        self.assertIs(Condition('Near Mint').finish, Finishes.NON_FOIL)

    def test_reads_the_language(self):
        # Only Japanese used to be listed, so every other foreign card read as English.
        for string, expected in [('Near Mint', Languages.ENGLISH),
                                 ('Near Mint Foil - Japanese', Languages.JAPANESE),
                                 ('Near Mint Foil - Chinese (S)', Languages.CHINESE_SIMPLIFIED),
                                 ('Near Mint Foil - Chinese (T)', Languages.CHINESE_TRADITIONAL),
                                 ('Damaged - Korean', Languages.KOREAN),
                                 ('Near Mint - Russian', Languages.RUSSIAN)]:
            with self.subTest(string=string):
                self.assertIs(Condition(string).language, expected)

    def test_keeps_the_original_string_for_writing_back(self):
        self.assertEqual(Condition('Near Mint Foil - Chinese (S)').string, 'Near Mint Foil - Chinese (S)')

    def test_an_unrecognised_condition_says_so(self):
        # This used to leave self.condition unset, so the next attribute access
        # raised AttributeError from somewhere unrelated.
        for string in ('', 'Mint-ish'):
            with self.subTest(string=string):
                with self.assertRaises(ValueError) as raised:
                    Condition(string)
                self.assertIn(repr(string), str(raised.exception))

    def test_knows_what_is_sealed(self):
        self.assertTrue(Condition('Unopened').is_sealed())
        self.assertFalse(Condition('Near Mint').is_sealed())


if __name__ == '__main__':
    unittest.main()
