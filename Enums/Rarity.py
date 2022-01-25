# Copyright (c) 2022, Richard Neal
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

from enum import Enum


class Rarity(Enum):
    MYTHIC = 'M'
    RARE = 'R'
    UNCOMMON = 'U'
    COMMON = 'C'

    PROMOTIONAL = 'P'
    TOKEN = 'T'
    SPECIAL = 'S'
    LAND = 'L'

    PRODUCT = ''
