import Utilities.bot_icons as icons

def text(data: dict = {}):
    return (
        {
            'General': {
                'loading': f'[ {icons.loading()} Loading {data.get("what", "")} ]',
                'loading_cmd': f'[ {icons.loading()} **Thinking...** ]'
            },
            
            'Shop': {
                
                'user_wool': f'You currently have: {icons.wool()}**{data.get("wool", "")}**',
                'go_back': 'Go back',
                
                'MainShop': {
                    'title': 'Welcome to the Shop!',
                
                    'description': f'''
                    Hey, Hey! Welcome to my emporium. I'm here always looking for the most interesting of treasures and {icons.wool()}**Wool**...! I'm willing to trade many shiny and colorful treasures, background, capsules and more for your wool... think of it as a currency eh?

                    {data.get("motd", "")}

                    **Here is my treasure stock for today:**
                    {data.get("treasure_stock", "")}
                    **Here is my background stock for today:**
                    {data.get("background_stock", "")}
                    {data.get("user_wool", "")}
                    ''',
                    
                    'motds': [
                        "Hm... people have a *real* knack for the **the wool market** for whatever reason...",
                        "By the way... is that what I think it is? More wool? More for me to ste- I mean trade?",
                        "I may have *broken* the wool market once or twice. Don't tell the feds.",
                        "Did you know? If you buy high and sell low, there will good fortune? Don't fact check that."
                    ],
                    
                    'buttons': {
                        'capsules': 'Capsules',
                        'pancakes': 'Pancakes',
                        'backgrounds': 'Backgrounds',
                        'treasures': 'Treasures',
                    }
                },
                
                'Capsules': {
                    'title': 'Capsules',
                
                    'description': f'''
                    
                    ''',
                    
                    'button': 'Buy',
                },
                
                'Pancakes': {
                    'title': 'Pancakes',
                    
                    'description': f'''
                    
                    '''
                    
                    'button': 'Buy',
                },
                
                'Backgrounds': {
                    'title': 'Backgrounds',
                    
                    'description': f'Do you want to buy **{data.get("name", "")}** for {icons.wool()}{data.get("price", "")}?',
                    
                    'button': 'Buy',
                }
            },
            
            'Items': {
                'Treasures': {
                    'bottle': {
                        'name': 'Bottle of Alcohol',
                        'description': 'The smell of the liquid is repugnant. Good for Molotov Cocktails.'
                    },
                    'shirt': {
                        'name': 'Novelty Shirt',
                        'description': '"I herded rams and all I got was this lousy T-shirt!"'
                    },
                    'journal': {
                        'name': 'Mysterious Journal',
                        'description': 'It\'s written in an unknown language.'
                    },
                    'amber': {
                        'name': 'Amber Medallion',
                        'description': 'A piece of glowing amber with a black clover inside.'
                    },
                    'pen': {
                        'name': 'Glowing Pen',
                        'description': 'A long and slender feather with glowing edges.'
                    },
                    'card': {
                        'name': '"Real" Library card',
                        'description': 'Niko\'s own photo is glued on.'
                    },
                    'die': {
                        'name': 'Glowing Die',
                        'description': 'A die with glowing dots.'
                    },
                    'sun': {
                        'name': 'Lightbulb',
                        'description': 'A large lightbulb. It\'s the sun.'
                    },
                    'clover': {
                        'name': 'Glowing Clover',
                        'description': 'A clover. It\'s glowing a golden hue.'
                    }
                },

                'Capsules': {
                    'blue': {
                        'name': 'Blue Capsule',
                        'description': 'Teeming with blue phosphor, this capsule will give you a common Nikogotchi.'
                    },
                    'green': {
                        'name': 'Green Capsule',
                        'description': 'Teeming with green phosphor, this capsule will give you an uncommon Nikogotchi.'
                    },
                    'red': {
                        'name': 'Red Capsule',
                        'description': 'Teeming with red phosphor, this capsule will give you a rare Nikogotchi.'
                    },
                    'yellow': {
                        'name': 'Yellow Capsule',
                        'description': 'Teeming with yellow phosphor, this capsule will give you an extra rare Nikogotchi.'
                    }
                },
                
                'Pancakes': {
                    'normal': {
                        'name': 'Pancake',
                        'description': '+1 Health and +25 Hunger'
                    },
                    'golden': {
                        'name': 'Golden Pancake',
                        'description': '+25 Health and +50 Hunger'
                    },
                    'glitched': {
                        'name': '???',
                        'description': 'I don\'t even know how this got here.'
                    }
                },
                
                'Backgrounds': {
                    'Normal': 'Normal',
                    'Green': 'Green',
                    'Yellow': 'Yellow',
                    'Pink': 'Pink',
                    'Red': 'Red',
                    'Blue': 'Blue',
                    'Barrens': 'Barrens',
                    'Glens': 'Glens',
                    'Refuge': 'Refuge',
                    'The Author': 'The Author',
                    'The World Machine': 'The World Machine',
                    'Alula and Calamus': 'Alula and Calamus',
                    'Pancakes': 'Pancakes'
                }
            }
        }
    )