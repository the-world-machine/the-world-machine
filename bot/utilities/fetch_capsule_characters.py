from enum import Enum


class Rarity(Enum):
    blue = 0
    green = 1
    red = 2
    yellow = 3


class Nikogotchi:
    # Nikogotchi Information
    name: str
    emoji: int
    rarity: Rarity

    def __init__(self, name: str, emoji: int, rarity: Rarity):
        self.name = name
        self.emoji = emoji
        self.rarity = rarity


def create_common_nikogotchi():

    return [
        Nikogotchi(
            "Prophet Bot",
            1147182670892253247,
            Rarity.blue
        ),
        Nikogotchi(
            "Silver",
            1147176557467672616,
            Rarity.blue
        ),
    ]


def create_uncommon_nikogotchis():

    return [
        Nikogotchi(
            "Alula",
            1147176544259801189,
            Rarity.green
        ),
        Nikogotchi(
            "Calamus",
            1147176547464253471,
            Rarity.green
        ),
        Nikogotchi(
            "Magpie",
            1147176551285272597,
            Rarity.green
        )
    ]


def create_rare_nikogotchis():

    return [
        Nikogotchi(
            "Lamplighter",
            1147182659798319175,
            Rarity.red
        ),
        Nikogotchi(
            "Watcher",
            1146965094845136946,
            Rarity.red
        ),
        Nikogotchi(
            "Ling",
            1147183240063500348,
            Rarity.red
        ),
        Nikogotchi(
            "Kelvin",
            1146967527512100925,
            Rarity.red
        ),
        Nikogotchi(
            "Kip",
            1147182658540032051,
            Rarity.red
        ),
        Nikogotchi(
            "Penguin",
            1147182669562654851,
            Rarity.red
        ),
        Nikogotchi(
            "George",
            1147183958279323759,
            Rarity.red
        )
    ]


def create_epic_nikogotchis():

    return [
        Nikogotchi(
            "Rue",
            1147182674964906077,
            Rarity.yellow
        ),
        Nikogotchi(
            "Prototype",
            1147182673673076828,
            Rarity.yellow
        ),
        Nikogotchi(
            "Cedric",
            1147182656191205396,
            Rarity.yellow
        ),
        Nikogotchi(
            "The World Machine",
            1147182676021878887,
            Rarity.yellow
        ),
        Nikogotchi(
            "Niko",
            1147176553655058492,
            Rarity.blue
        ),
    ]

def get_characters():
    char1 = create_common_nikogotchi()
    char2 = create_uncommon_nikogotchis()
    char3 = create_rare_nikogotchis()
    char4 = create_epic_nikogotchis()

    return char1 + char2 + char3 + char4
