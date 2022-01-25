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
