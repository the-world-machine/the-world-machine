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
            "stock": f'*Stock Value:* `{fetch("stock_value")}`\n*Stock Price:* `{fetch("stock_price")}`',
            
            "key_owned": '🔴 - Already Owned \n ⚪ - Cannot Afford',
            "key_general": '⚪ - Cannot Afford',
            
            "go_back": "Go back",  # Button for when a user wants to go back to the main shop.
            "buy": "Trade",  # Button for when a user buys something.
            "buy_all": "Trade All",

            "sell_button": "Sell Treasures",
            "sell": "Sell One",
            "sell_all": "Sell All",
            
            "cannot_buy": "You do not have enough to trade for this item.",
            "cannot_sell": "You do not have anything to trade.",
            "already_owned": "You already own this item.",
            
            "bought": f'Successfully traded {fetch("cost")} Wool for {fetch("what")}!',
            "bought_all": f'Successfully traded {fetch("cost")} Wool for {fetch("amount")} {fetch("what")}(s)!',
            
            "sold": f'Successfully sold {fetch("what")} for {fetch("cost")} Wool!',
            "sold_all": f'Successfully sold {fetch("amount")} {fetch("what")}(s) for {fetch("cost")} Wool!',
            
            "currently_owned": f'Currently owned: **{fetch("amount")}**',
            
            "MainShop": {
                "title": "Welcome to the Shop!",
                
                "description": f"""
                    Hey, Hey! Welcome to my emporium. I'm here always looking for the most interesting of treasures and {wool_icon}**Wool**...! I'm willing to trade many shiny and colorful treasures, background, capsules and more for your wool... think of it as a currency eh?

                    To get started, simply select on one of the categories I have presented and then trade away! Keep in mind there are some items that change **daily** so keep an eye on those!
                    
                    {fetch("motd")}
                    
                    {fetch("user_wool")}
                    """,
                    
                "motds": [
                    "The wool market changes everyday. Honestly, we bird people have a good intuition about it, and by intuition I mean I randomly increase it or decrease it to whatever I feel like.",
                    "I may have *broken* the wool market once or twice. Let's keep that between us.",
                    "Words of wisdom as a friend: If you buy high and sell low, good fortune awaits..! Don't fact check that!",
                    "My poor trinket and treasures were washed away... perhaps you could find more for me?",
                    "You're asking about what happened to that one trader before me? I wouldn't know. I wouldn't know at all...", # During the World Machine Edition AMA Nightmargin jokingly said that Magpie hid a body which has not been found yet. Considering the fact that the purple trader is nowhere to be found in the remake, it is the most likely victim of this alleged crime.
                    "Do you like my bottle collection? I like my bottle collection. What do you mean it's all \"Hard Liquor\"? Is that what it says?", # Magpie's drink of choice is hard liquor, but only so he can collect the bottles afterwards.
                ],
                
                "buttons": {
                    # Translate right hand values (e.g. 'capsules': 'ガチャポン')
                    "capsules": "Capsules",
                    "pancakes": "Pancakes",
                    "Backgrounds": "Backgrounds",
                    "Treasures": "Treasures",
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
                "description": f'Do you want to buy **{fetch("name")}** for {wool_icon}{fetch("cost")}?\n\n{fetch("key")}\n\n{fetch("user_wool")}',
            },
            
            "Treasures": {
                "title": "Treasures",
                "description": f"""
                Woah! It seems you're quite interested in my treasure collection. I've gathered these goodies from all sorts of traders from all across the world, from the Barrens to even the Refuge!
                
                You can take these shiny and fantastical treasures off of my feathers all just for some of your wool!!

                Oh! and of course, you can trade in your own treasure as well to get wool back... think of it as 'selling' your treasures.

                Keep in mind that the wool stock market changes every day, so be sure to constantly check for opportunities!
                
                ***Wool Market:***
                
                {fetch('wool_market')}

                ***Treasure Stock:***
                {fetch('treasures')}
                
                {fetch('key')}
                {fetch('user_wool')}
                """
            },
            
            "Treasure_Sell": {
                "title": "Sell Treasures",
                "description": f"""
                Ah... Looking to trade some treasures for some of my {wool_icon}Wool? Well, you're in luck!
                
                Just select the treasure and how much you want to sell!
                
                Just keep in mind that the *wool market* affects how much wool you'll get back.
                
                ***Wool Market:***
                
                {fetch('wool_market')}
                
                ***Selected Treasure:***
                
                {fetch('selected_treasure')}
                
                {fetch('currently_owned')}
                
                
                {fetch('user_wool')}
                """,
                
                "select_no_treasures :(": f"You don't have any treasures!",
                "select_treasure_placeholder": f"Select a treasure!",
            
                "treasure_not_selected": "It seems you haven't selected any treasure yet. I'll let you know when you do!",
                "treasure_selected": f"""
                **{fetch('selected_treasure')}**
                Sell One: {wool_icon}{fetch('sell_one')}
                Sell All: {wool_icon}{fetch('sell_all')}
                """,
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
            "Backgrounds": {
                # Translate the right hand value. (e.g. 'Normal': 'Translate This.')
                "Default": "Default",
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
                "Magpie": "Magpie",
                "Catwalk": "Catwalk",
                "Ruins": "Ruins",
                "Factory": "Factory",
                "Lamplighter": "Lamplighter",
                "Library": "Library",
            },
        },
    }
