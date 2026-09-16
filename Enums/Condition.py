# Copyright (c) 2022, Richard Neal
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

from enum import Enum


class Languages(Enum):
    # English is the default, and is the one language TCGPlayer does not name in
    # the condition string, so its value is empty and it is never matched on.
    ENGLISH = ''

    CHINESE_SIMPLIFIED = 'Chinese (S)'
    CHINESE_TRADITIONAL = 'Chinese (T)'
    FRENCH = 'French'
    GERMAN = 'German'
    ITALIAN = 'Italian'
    JAPANESE = 'Japanese'
    KOREAN = 'Korean'
    PORTUGUESE = 'Portuguese'
    RUSSIAN = 'Russian'
    SPANISH = 'Spanish'


class Finishes(Enum):
    NON_FOIL = ''
    FOIL = 'Foil'


class Conditions(Enum):
    NEAR_MINT = 'Near Mint'
    LIGHTLY_PLAYED = 'Lightly Played'
    MODERATELY_PLAYED = 'Moderately Played'
    HEAVILY_PLAYED = 'Heavily Played'
    DAMAGED = 'Damaged'

    UNOPENED = 'Unopened'


class Condition:
    condition: Conditions
    finish: Finishes
    language: Languages
    string: str

    def __init__(self, condition_str: str):
        self.string = condition_str
        self.condition = self._parse_condition(condition_str)

        if Finishes.FOIL.value in condition_str:
            self.finish = Finishes.FOIL
        else:
            self.finish = Finishes.NON_FOIL

        self.language = self._parse_language(condition_str)

    @staticmethod
    def _parse_condition(condition_str: str) -> Conditions:
        for condition_enum in Conditions:
            if condition_enum.value in condition_str:
                return condition_enum
        raise ValueError(f'{condition_str!r} is not a valid Condition')

    @staticmethod
    def _parse_language(condition_str: str) -> Languages:
        for language in Languages:
            # English has no marker in the condition string, so it is the fallback.
            if language.value and language.value in condition_str:
                return language
        return Languages.ENGLISH

    def is_sealed(self):
        return self.condition is Conditions.UNOPENED
