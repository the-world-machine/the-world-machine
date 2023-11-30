import Utilities.bot_icons as icons


def text(data: dict = {}):
    
    # Generally, you want to leave this code alone. Unless you want to do something fancy.
    def fetch(what: str):
        return data.get(what, "")

    # Simply renaming variables so that it makes things easier to read.
    loading_icon = icons.loading()
    wool_icon = icons.wool()

    # Start of translations
    return {
        "General": {
            "loading": f"[ {loading_icon} **Loading...** ]",
            "loading_cmd": f"[ {loading_icon} **Thinking...** ]",
        },
        
        "Shop": {
            "user_wool": f'You currently have: {wool_icon}**{fetch("wool")}**',
            "stock": f'**Stock Value:** `{fetch("stock_value")}`\n**Stock Price:** {fetch("stock_price")}',
            
            "key_owned": '🔴 - Already Owned \n ⚪ - Cannot Afford',
            "key_general": '⚪ - Cannot Afford',
            
            "go_back": "Go back",  # Button for when a user wants to go back to the main shop.
            "buy": "Buy",  # Button for when a user buys something.
            
            "cannot_buy": "You cannot afford this item.",
            "cannot_sell": "You cannot sell this item.",
            "already_owned": "You already own this item.",
            
            "bought": f'Successfully bought {fetch("what")} for {fetch("cost")} Wool!',
            
            "currently_owned": f'Currently owned: **{fetch("amount")}**',
            
            "MainShop": {
                "title": "Welcome to the Shop!",
                
                "description": f"""
                    Hey, Hey! Welcome to my emporium. I'm here always looking for the most interesting of treasures and {wool_icon}**Wool**...! I'm willing to trade many shiny and colorful treasures, background, capsules and more for your wool... think of it as a currency eh?

                    {fetch("motd")}

                    **Here is my treasure stock for today:**
                    {fetch("treasure_stock")}
                    **Here is my background stock for today:**
                    {fetch("background_stock")}
                    {fetch("user_wool")}
                    """,
                    
                "motds": [
                    "Hm... people have a *real* knack for the the wool market for whatever reason...",
                    "By the way... is that what I think it is? More wool? More for me to ste- I mean trade?",
                    "I may have *broken* the wool market once or twice. Don't tell the feds.",
                    "Did you know? If you buy high and sell low, there will good fortune? Don't fact check that.",
                ],
                
                "buttons": {
                    # Translate right hand values (e.g. 'capsules': 'ガチャポン')
                    "capsules": "Capsules",
                    "pancakes": "Pancakes",
                    "backgrounds": "Backgrounds",
                    "treasures": "Treasures",
                },
            },
            
            "Capsules": {
                "title": "Capsules",
                "description": f"""
                    Want a companion for your journey? Now you can by buying one of these capsules! By purchasing one, you can unlock a random **Nikogotchi** to take care of! The rarer the capsule, the cooler the Nikogotchi!
        
                    After purchasing a Nikogotchi, run the </nikogotchi check:1149412792919674973> command to see your new friend! Make sure to take care of them, as if any of their needs are not met, they will lose health and die...
                    
                    By feeding them using pancakes, giving them attention and cleaning them, your Nikogotchi will live for a very long time! Cleaning them and giving them attention is easy enough, but you'll need to buy pancakes from me!
                    
                    Just keep in mind that you can only have one Nikogotchi at a time. The only way to get another one is to  send away your current one or if it has passed away.
                    
                    {fetch("capsules")}
                    {fetch("key")}
                    
                    {fetch("user_wool")}
                    """,
            },
            
            "Pancakes": {
                "title": "Pancakes",
                "description": f"""
                    Use these pancakes to feed your Nikogotchi! They have various effect from making your Nikogotchi happy to completely healing them from all ailments!
                    
                    {fetch("pancakes")}
                    {fetch("key")}
                    
                    {fetch("user_wool")}
                    """,
            },
            
            "Backgrounds": {
                "title": "Backgrounds",
                "description": f'Do you want to buy **{fetch("name")}** for {wool_icon}{fetch("cost")}?\n\n{fetch("key")}',
            },
        },
        "Items": {
            # Translate 'name' and 'description' values.
            "Treasures": {
                "bottle": {
                    "name": "Bottle of Alcohol",
                    "description": "The smell of the liquid is repugnant. Good for Molotov Cocktails.",
                },
                "shirt": {
                    "name": "Novelty Shirt",
                    "description": '"I herded rams and all I got was this lousy T-shirt!"',
                },
                "journal": {
                    "name": "Mysterious Journal",
                    "description": "It's written in an unknown language.",
                },
                "amber": {
                    "name": "Amber Medallion",
                    "description": "A piece of glowing amber with a black clover inside.",
                },
                "pen": {
                    "name": "Glowing Pen",
                    "description": "A long and slender feather with glowing edges.",
                },
                "card": {
                    "name": '"Real" Library card',
                    "description": "Niko's own photo is glued on.",
                },
                "die": {
                    "name": "Glowing Die",
                    "description": "A die with glowing dots.",
                },
                "sun": {
                    "name": "Lightbulb",
                    "description": "A large lightbulb. It's the sun.",
                },
                "clover": {
                    "name": "Glowing Clover",
                    "description": "A clover. It's glowing a golden hue.",
                },
            },
            "capsules": {
                "blue": {
                    "name": "Blue Capsule",
                    "description": "Teeming with blue phosphor, this capsule will give you a common Nikogotchi.",
                },
                "green": {
                    "name": "Green Capsule",
                    "description": "Teeming with green phosphor, this capsule will give you an uncommon Nikogotchi.",
                },
                "red": {
                    "name": "Red Capsule",
                    "description": "Teeming with red phosphor, this capsule will give you a rare Nikogotchi.",
                },
                "yellow": {
                    "name": "Yellow Capsule",
                    "description": "Teeming with yellow phosphor, this capsule will give you an extra rare Nikogotchi.",
                },
            },
            "pancakes": {
                "pancakes": {
                    "name": "Pancake",
                    "description": "+1 Health and +25 Hunger",
                },
                "golden_pancakes": {
                    "name": "Golden Pancake",
                    "description": "+25 Health and +50 Hunger",
                },
                "glitched_pancakes": {
                    "name": "???",
                    "description": "I don't even know how this got here.",
                },
            },
            "backgrounds": {
                # Translate the right hand value. (e.g. 'Normal': 'Translate This.')
                "Normal": "Normal",
                "Green": "Green",
                "Yellow": "Yellow",
                "Pink": "Pink",
                "Red": "Red",
                "Blue": "Blue",
                "Barrens": "Barrens",
                "Glens": "Glens",
                "Refuge": "Refuge",
                "The Author": "The Author",
                "The World Machine": "The World Machine",
                "Alula and Calamus": "Alula and Calamus",
                "Pancakes": "Pancakes",
            },
        },
    }
