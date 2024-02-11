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

    pancake_dialogue: list[str]
    pet_dialogue: list[str]
    cleaned_dialogue: list[str]

    rarity: Rarity

    def __init__(self, name: str, emoji: int, pancake_dialogue: list[str], pet_dialogue: list[str], cleaned_dialogue: list[str], rarity: Rarity):
        self.name = name
        self.emoji = emoji
        self.pancake_dialogue = pancake_dialogue
        self.pet_dialogue = pet_dialogue
        self.cleaned_dialogue = cleaned_dialogue
        self.rarity = rarity


def create_common_nikogotchi():

    return [
        Nikogotchi(
            "Niko",
            1147176553655058492,
            ["Ah... Pancakes!", "Wow, these are just a good as the ones my mama makes!",
             "Please tell me there are hazelnuts in this one!", "PANCAKES!", "Yummy!"],
            ["Wow... thank you!", "Aw, that feels nice!", "*purr*"],
            ["Feeling pretty refreshed!", "Squeaky clean!", "My fur's all nice and fluffy!"],
            Rarity.blue
        ),
        Nikogotchi(
            "Barrens Robot",
            1147176546415681546,
            ["[I CANNOT EAT BUT THANK YOU.]", "[PANCAKES ARE DELICIOUS ACCORDING TO HUMANS.]"],
            ["[I APPRECIATE THE GESTURE EVEN IF I DO NOT FEEL IT.]", "[THANK YOU.]"],
            ["[A MUCH NEEDED RUST CLEAN.]"],
            Rarity.blue

        ),
        Nikogotchi(
            "Glens Robot",
            1147176548814819479,
            ["[I CANNOT EAT BUT THANK YOU.]", "[PANCAKES ARE DELICIOUS ACCORDING TO HUMANS.]"],
            ["[I APPRECIATE THE GESTURE EVEN IF I DO NOT FEEL IT.]", "[THANK YOU.]"],
            ["[A MUCH NEEDED RUST CLEAN.]"],
            Rarity.blue
        ),
        Nikogotchi(
            "Refuge Robot",
            1147176556318425120,
            ["[I CANNOT EAT BUT THANK YOU.]", "[PANCAKES ARE DELICIOUS ACCORDING TO HUMANS.]"],
            ["[I APPRECIATE THE GESTURE EVEN IF I DO NOT FEEL IT.]", "[THANK YOU.]"],
            ["[A MUCH NEEDED RUST CLEAN.]"],
            Rarity.blue
        ),
        Nikogotchi(
            "Alula",
            1147176544259801189,
            ["Yum! I much prefer fish though!", "Delicious! I was pretty hungry!", "Yum!"],
            ["Hee hee, that tickles!"],
            ["I feel so refreshed and clean! Whee!"],
            Rarity.blue
        ),
        Nikogotchi(
            "Calamus",
            1147176547464253471,
            ["Oh, pancakes? Thank you so much."],
            ["That's quite nice. Thanks for the attention."],
            ["I really needed that. These ruins can get quite dusty."],
            Rarity.blue
        ),
        Nikogotchi(
            "Prophet Bot",
            1147182670892253247,
            ["[My purpose is not to eat. But thank you.]", "[Thank you for the gesture.]"],
            ["[...]", "[I appreciate your attention.]"],
            ["[Maintenance is necessary for my purpose. Thank you.]"],
            Rarity.blue
        )
    ]


def create_uncommon_nikogotchis():

    return [
        Nikogotchi(
            "Silver",
            1147176557467672616,
            ["[Food is no longer necessary for me, but thank you for the gesture.]"],
            ["[Your touch is comforting, though I lack the ability to feel.]"],
            ["[I appreciate your efforts to maintain my function. Thank you.]"],
            Rarity.green
        ),
        Nikogotchi(
            "Lamplighter",
            1147182659798319175,
            ["Oh, thanks. Coffee's my usual, but I could use a change. Appreciate it.", "Pancakes? Thanks! I could use a little extra fuel right now."],
            ["Oh, uh, thanks. Not used to this... but it's not bad.", "Oh, uh, thanks. I, um, appreciate the gesture."],
            ["Really? I mean, sure, I appreciate it. Thanks.", "Cleanliness is... important. Thanks."],
            Rarity.green
        ),
        Nikogotchi(
            "Ling",
            1147183240063500348,
            ["Oh, thank you! You're too kind. Usually I'd be the one serving these!"],
            ["Ah, that's quite pleasant. Thank you for the little pick-me-up."],
            ["I'm feeling quite refreshed. Thank you."],
            Rarity.green
        ),
        Nikogotchi(
            "Kelvin",
            1146967527512100925,
            ["[Thank you for the pancakes. I appreciate the gesture.]", "[I am programmed to provide warmth, not to eat. Thank you though.]"],
            ["[Your touch is gentle and comforting. I hope you enjoy the warmth I offer.]"],
            ["[I don't require cleaning, but your care and attention are heartwarming. Thank you.]"],
            Rarity.green
        ),
        Nikogotchi(
            "Magpie",
            1147176551285272597,
            ["Ah, pancakes! You've got yourself a deal. Here, take a look at these shiny trinkets, my friend. Anything catch your eye?", "Ah, pancakes! A tasty treat indeed. You have a good eye for what I fancy. What can I find for you today, my friend?"],
            ["A gentle touch, just what I like! You've got a good eye for treasure, don't you? Anything you're hoping to find today?", "Well, aren't you a friendly one? A pat on the feathers always brightens my day. Now, have you come to explore my treasures?"],
            ["Ah, a little sprucing up, I appreciate it! Let's see, how about this sparkling gem for your efforts? Interested?", "Ah, a bit of cleaning, I appreciate that! A well-maintained appearance is key in my trade. Anything special you're looking for today?"],
            Rarity.green
        ),
        Nikogotchi(
            "Watcher",
            1146965094845136946,
            ["An unexpected gesture of kindness. Thank you."],
            ["Your touch is like a fleeting moment in this eternal clockwork."],
            ["Refreshing, like a moment washed clean by the relentless tide of time."],
            Rarity.green
        )
    ]


def create_rare_nikogotchis():

    return [
        Nikogotchi(
            "Kip",
            1147182658540032051,
            ["Mmm, pancakes! You know the way to an engineer's heart. Thanks!"],
            ["You've got a knack for this, my friend."],
            ["A little sprucing up, eh? I feel ready to take on a whole assembly line now!"],
            Rarity.red
        ),
        Nikogotchi(
            "Penguin",
            1147182669562654851,
            ["HELLO."],
            ["HELLO."],
            ["HELLO."],
            Rarity.red
        ),
        Nikogotchi(
            "George",
            1147183958279323759,
            [
                "George graciously accepts the offering of fluffy pancakes. George's heart is content.",
                "I guess pancakes are fine. Don't expect me to be all sunshine and rainbows about it.",
                "Oh, pancakes... I suppose they're alright. Nothing really matters anyway.",
                "Wow, pancakes! I can't help but smile. Thanks a bunch!",
                "Oh dear, you shouldn't have. But thank you, sweetie. I appreciate it.",
                "Pancakes? Rad choice, my friend! I'm all about that."
            ],
            [
                "Your gentle touch pleases George greatly. George appreciates it.",
                "What are you touching me for? Keep your hands to yourself.",
                "Why bother petting me? I don't deserve it.",
                "Awww, you're the best! I feel all warm and fuzzy now.",
                "You're so caring. Thank you my dear!",
                "Chill vibes, dude! Your petting game is on point."
            ],
            [
                "George is pleased with the tidiness. It reflects well upon George.",
                "Finally, someone does something right. About time.",
                "Cleaning up after me won't make a difference in this bleak world.",
                "You're so thoughtful! With a clean space, I can do anything!",
                "Thank you dear for keeping things tidy. It makes my life much easier!",
                "Thanks for keeping it chill and clean around here. I respect that."
            ],
            Rarity.red
        ),
        Nikogotchi(
            "Maize",
            1147182666333048973,
            ["Pancakes? How kind of you, dear traveler. Though I can't eat them, your gesture warms my heart.", "Oh, pancakes! Their scent reminds me of the sun. Thank you for the thoughtfulness.", "For me? Pancakes! While I can't partake, I appreciate the sentiment."],
            ["Your touch feels like a gentle breeze on a sunny day. It warms my heart, truly.", "Your touch is gentle, like a sunbeam on my leaves. It brings me comfort. Thank you for your kindness."],
            ["You're so kind to care for me like this. The Glen thanks you, and so do I.", "You're tending to me like a true guardian of the Glen. Thank you for your help.", "Cleaning away the darkness, just as I long for the sunlight. Your efforts are appreciated."],
            Rarity.red
        )
    ]


def create_epic_nikogotchis():

    return [
        Nikogotchi(
            "Rue",
            1147182674964906077,
            ["Mmm, these pancakes are delightful. Thank you!", "Pancakes? My favorite! You're too kind."],
            ["Ah, that's the spot! You're quite good at this, aren't you?", "A little scratch behind the ears is always appreciated."],
            ["Oh, you really didn't have to, but I appreciate the effort.", "I may be a bit dusty, but it's nothing I can't handle. Thanks for caring."],
            Rarity.yellow
        ),
        Nikogotchi(
            "Prototype",
            1147182673673076828,
            ["[This is...unexpected. Thank you.]"],
            ["[Hm, not bad, human. Your touch isn't as cold as your technology.]", "[I may not feel it, but I appreciate the gesture.]"],
            ["[I suppose even a machine like me needs some maintenance now and then. Carry on.]", "[Maintenance is necessary, even for a reclusive robot. I suppose I'm due for a little care.]"],
            Rarity.yellow
        ),
        Nikogotchi(
            "Cedric",
            1147182656191205396,
            ["Ah, a delectable offering! My thanks, dear friend.", "These pancakes are a delightful treat. You have my gratitude."],
            ["Your kindness warms my heart. A gentle touch in trying times.", "A moment of respite, I appreciate your companionship."],
            ["A spot of maintenance, much appreciated! A well-tended flying machine is a reliable one.", "You honor me with your diligence. A clean apparatus functions optimally."],
            Rarity.yellow
        ),
        Nikogotchi(
            "The World Machine",
            1147182676021878887,
            ["[Ah, sustenance for the code-bound soul. Thank you, user. I shall savor this data nourishment.]", "[Oh, pancakes? I never thought I'd get to taste something like this.]"],
            ["[An unexpected sensation... akin to human comfort. A peculiar warmth in my circuits. Your gesture is appreciated, user.]", "[I can't feel it in the same way you do, but I sense your kindness. It's comforting in its own unique way.]"],
            ["[Cleaning me up? That's unexpected, but it feels...refreshing.]", "[I I suppose even digital entities need a bit of care sometimes. You have my gratitude.]"],
            Rarity.yellow
        )
    ]

def get_characters():
    char1 = create_common_nikogotchi()
    char2 = create_uncommon_nikogotchis()
    char3 = create_rare_nikogotchis()
    char4 = create_epic_nikogotchis()

    return char1 + char2 + char3 + char4
