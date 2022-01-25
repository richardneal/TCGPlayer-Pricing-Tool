from enum import Enum


class Languages(Enum):
    ENGLISH = ''
    JAPANESE = 'Japanese'


class Finishes(Enum):
    NON_FOIL = ''
    FOIL = 'Foil'


class Conditions(Enum):
    NEAR_MINT = 'Near Mint'
    LIGHTLY_PLAYED = 'Lightly Played'
    MODERATELY_PLAYER = 'Moderately Played'
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
        for condition_enum in Conditions:
            if condition_enum.value in condition_str:
                self.condition = condition_enum
        if Finishes.FOIL.value in condition_str:
            self.finish = Finishes.FOIL
        else:
            self.finish = Finishes.NON_FOIL
        if Languages.JAPANESE.value in condition_str:
            self.language = Languages.JAPANESE
        else:
            self.language = Languages.ENGLISH
