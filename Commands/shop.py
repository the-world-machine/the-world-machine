from datetime import datetime, timedelta

from interactions import *
from Utilities.fancysend import *
from Commands.shop_callbacks import setup_callbacks
from Utilities.FetchShopData import fetch_shop_data
import Utilities.badge_manager as badge_manager
import Utilities.bot_icons as icons
import database
import aiofiles
import json
import random


class Command(Extension):
    def get_shop_buttons(self):

        return [
            Button(
                style=ButtonStyle.PRIMARY,
                label='Buy Capsules',
                custom_id='shop_capsules',
                emoji=PartialEmoji(id=1147279938660089898),
            ),
            Button(
                style=ButtonStyle.PRIMARY,
                label='Buy Pancakes',
                custom_id='shop_pancakes',
                emoji=PartialEmoji(id=1147281411854839829),
            ),
            Button(
                style=ButtonStyle.PRIMARY,
                label='Buy Backgrounds',
                custom_id='shop_backgrounds',
                emoji=PartialEmoji(id=1026181558392062032),
            ),
            Button(
                style=ButtonStyle.PRIMARY,
                label='Treasures',
                custom_id='shop_treasures',
                emoji=PartialEmoji(id=1026181503597678602),
            )
        ]

    def get_treasure_buttons(self):

        return [
            Button(
                style=ButtonStyle.PRIMARY,
                label='Buy',
                custom_id='buy_treasure_1',
            ),
            Button(
                style=ButtonStyle.PRIMARY,
                label='Buy',
                custom_id='buy_treasure_2',
            ),
            Button(
                style=ButtonStyle.PRIMARY,
                label='Buy',
                custom_id='buy_treasure_3',
            ),
            Button(
                style=ButtonStyle.PRIMARY,
                label='Sell Treasures',
                custom_id='sell_treasures',
            ),
            Button(
                style=ButtonStyle.RED,
                label='Go Back',
                custom_id='go_back'
            )
        ]

    def get_capsules_buttons(self):

        return [
            Button(
                style=ButtonStyle.PRIMARY,
                label='Buy',
                custom_id='buy_blue',
                emoji=PartialEmoji(id=1147279938660089898),
            ),
            Button(
                style=ButtonStyle.PRIMARY,
                label='Buy',
                custom_id='buy_green',
                emoji=PartialEmoji(id=1147279943387070494),
            ),
            Button(
                style=ButtonStyle.PRIMARY,
                label='Buy',
                custom_id='buy_red',
                emoji=PartialEmoji(id=1147280712328810536),
            ),
            Button(
                style=ButtonStyle.PRIMARY,
                label='Buy',
                custom_id='buy_yellow',
                emoji=PartialEmoji(id=1147279947086438431),
            ),
            Button(
                style=ButtonStyle.RED,
                label='Go Back',
                custom_id='go_back'
            )
        ]

    def get_background_buttons(self):

        return [
            Button(
                style=ButtonStyle.PRIMARY,
                label='<',
                custom_id='move_left'
            ),
            Button(
                style=ButtonStyle.PRIMARY,
                label='Buy',
                custom_id='buy_background',
            ),
            Button(
                style=ButtonStyle.RED,
                label='Go Back',
                custom_id='go_back'
            ),
            Button(
                style=ButtonStyle.PRIMARY,
                label='>',
                custom_id='move_right'
            ),
        ]

    buy_background_embed = Embed(
        title='Buy Backgrounds',
        color=0x8b00cc
    )

    main_shop_embed = Embed(
        title='Shop',
        color=0x8b00cc
    )

    buy_capsules_embed = Embed(
        title='Buy Capsules',
        color=0x8b00cc
    )

    async def get_backgrounds(self):

        async with aiofiles.open('Data/backgrounds.json', 'r') as f:
            raw_json = await f.read()

        return json.loads(raw_json)['background']

    current_background_stock = []
    current_treasure_stock = []
    current_stock_price = []

    async def check_if_should_reset(self):

        async with aiofiles.open('Data/last_shop_reset_date.json', 'r') as f:
            raw_json = await f.read()

        data = json.loads(raw_json)

        return data

    async def reset_data(self, data: dict):

        async with aiofiles.open('Data/last_shop_reset_date.json', 'w') as f:
            await f.write(json.dumps(data))

    def get_treasures(self):
        with open('Data/treasure.json', 'r') as f:
            data = f.read()

        return json.loads(data)
    async def shop_reset(self):
        data = await self.check_if_should_reset()

        current_time = datetime.now()
        reset_time = datetime.strptime(data['date'], '%Y-%m-%d %H:%M:%S')

        if current_time > reset_time:

            get_backgrounds: list[dict] = await self.get_backgrounds()

            backgrounds = []

            for bg in get_backgrounds:
                if bg['type'] == 'shop':
                    backgrounds.append(bg)

            background_1 = random.choice(backgrounds)
            backgrounds.remove(background_1)
            background_2 = random.choice(backgrounds)
            backgrounds.remove(background_2)
            background_3 = random.choice(backgrounds)

            treasure_stocks = []
            available_treasures: list = self.get_treasures()

            treasure_stocks = random.sample(range(len(available_treasures)), 3)

            stock_modifier = round(random.uniform(0.5, 1.5), 1)

            self.current_background_stock = [background_1, background_2, background_3]
            self.current_treasure_stock = treasure_stocks
            self.current_stock_price = stock_modifier

            # Reset the date to midnight of the next day.
            new_time = datetime(current_time.year, current_time.month, current_time.day, 00, 00, 00) + timedelta(days=1)

            await self.reset_data({
                "date": datetime.strftime(new_time, '%Y-%m-%d %H:%M:%S'),
                "backgrounds": [background_1, background_2, background_3],
                "treasure_stock": treasure_stocks,
                "stock_modifier": stock_modifier
            })

        else:
            self.current_background_stock = data['backgrounds']
            self.current_treasure_stock = data['treasure_stock']
            self.current_stock_price = data['stock_modifier']

    @listen()
    async def on_ready(self):
        await self.shop_reset()
        setup_callbacks(self)

    @slash_command(description='Open the shop!')
    async def shop(self, ctx: SlashContext):

        await fancy_message(ctx, f"[ Opening shop... {icons.loading()} ]", ephemeral=True)

        await self.shop_reset()

        embed, buttons = await self.get_main_shop(int(ctx.author.id))

        await ctx.edit(embed=embed, components=buttons)

    @component_callback('shop_capsules', 'shop_pancakes', 'shop_backgrounds', 'shop_treasures')
    async def shop_callback(self, ctx: ComponentContext):

        custom_id = ctx.custom_id

        embed, components = await self.get_main_shop(int(ctx.author.id))

        if custom_id == 'shop_capsules':
            embed, components = await self.get_capsules(int(ctx.author.id))

        if custom_id == 'shop_pancakes':
            embed, components = await self.get_pancakes(int(ctx.author.id))

        if custom_id == 'shop_backgrounds':
            embed, components = await self.open_backgrounds(int(ctx.author.id), 0)

        if custom_id == 'shop_treasures':
            embed, components = await self.open_treasures(int(ctx.author.id))

        await ctx.edit_origin(embed=embed, components=components)

    async def get_main_shop(self, uid: int):

        embed = self.main_shop_embed
        embed.description = f'''
        **Welcome to the shop!**
        
        Here you can exchange your {icons.wool()}Wool for some colorful and shiny backgrounds, capsules and more! You can even sell any sparkly treasures you find here too!
        
        Feel free to browse through the categories by clicking on one of the buttons, or simply exit the shop by dismissing this message.
        As a seasoned merchant and purveyor of fine goods, I can assure you that my stock is always worth checking out.

        {icons.wool()}**{database.fetch('user_data', 'wool', uid)}**
        '''

        embed.set_thumbnail('https://cdn.discordapp.com/attachments/1040653069794410567/1106652038772830238/Magpie.webp')
        buttons = self.get_shop_buttons()

        return embed, buttons

    async def get_capsules(self, uid: int):

        wool = database.fetch('user_data', 'wool', uid)
        badges = await badge_manager.open_badges()
        badges = badges['shop']

        shop_data = await fetch_shop_data()
        capsule_data = shop_data['Capsules']
        embed = self.buy_capsules_embed
        buttons = self.get_capsules_buttons()

        embed.thumbnail = 'https://cdn.discordapp.com/attachments/1040653069794410567/1106652038772830238/Magpie.webp'

        embed.description = f'''
        Want a companion for your journey? Now you can by buying one of these capsules! By purchasing one, you can unlock a random **Nikogotchi** to take care of! The rarer the capsule, the cooler the Nikogotchi!
        
        After purchasing a Nikogotchi, run the ``/nikogotchi check`` command to see your new friend! Make sure to take care of them, as if any of their needs are not met, they will lose health and die...
        
        By feeding them using pancakes, giving them attention and cleaning them, your Nikogotchi will live for a very long time! Cleaning them and giving them attention is easy enough, but you'll need to buy pancakes from me!
        
        Just keep in mind that you can only have one Nikogotchi at a time. The only way to get another one is to  send away your current one or if it has passed away.
        
        <:any:{capsule_data['Blue Capsule']['icon']}> **Blue Capsule** - ({icons.wool()}{capsule_data['Blue Capsule']['cost']})
        {capsule_data['Blue Capsule']['description']}
        
        <:any:{capsule_data['Green Capsule']['icon']}> **Green Capsule** - ({icons.wool()}{capsule_data['Green Capsule']['cost']})
        {capsule_data['Green Capsule']['description']}
        
        <:any:{capsule_data['Red Capsule']['icon']}> **Red Capsule** - ({icons.wool()}{capsule_data['Red Capsule']['cost']})
        {capsule_data['Red Capsule']['description']}
        
        <:any:{capsule_data['Yellow Capsule']['icon']}> **Yellow Capsule** - ({icons.wool()}{capsule_data['Yellow Capsule']['cost']})
        {capsule_data['Yellow Capsule']['description']}
        
        ⚪ - Cannot afford
        🔴 - Already owned
        
        {icons.wool()}**{wool}**
        '''

        for i, badge in enumerate(badges):
            if badge['requirement'] > wool:
                buttons[i].disabled = True
                buttons[i].style = ButtonStyle.GREY
            elif database.fetch('nikogotchi_data', 'data', uid) is not None:
                buttons[i].disabled = True
                buttons[i].style = ButtonStyle.DANGER
            else:
                buttons[i].disabled = False
                buttons[i].style = ButtonStyle.PRIMARY

        return embed, buttons

    async def get_pancakes(self, uid: int):

        wool = database.fetch('user_data', 'wool', uid)
        pancakes = database.fetch('nikogotchi_data', 'pancakes', uid)
        golden_pancakes = database.fetch('nikogotchi_data', 'golden_pancakes', uid)
        glitched_pancakes = database.fetch('nikogotchi_data', 'glitched_pancakes', uid)

        embed = Embed(
            title='Buy Pancakes',
            color=0x8b00cc
        )

        shop_data = await fetch_shop_data()
        pancake_data = shop_data['Pancakes']

        embed.set_thumbnail('https://cdn.discordapp.com/attachments/1040653069794410567/1106652038772830238/Magpie.webp')
        embed.description = f'''
        Use these pancakes to feed your Nikogotchi!
        
        <:any:{pancake_data['Pancake']['icon']}> **Pancake** - ({icons.wool()}{pancake_data['Pancake']['cost']})
        {pancake_data['Pancake']['description']} - Owned: **{pancakes}**
        
        <:any:{pancake_data['Golden Pancake']['icon']}> **Golden Pancake** - ({icons.wool()}{pancake_data['Golden Pancake']['cost']})
        {pancake_data['Golden Pancake']['description']} - Owned: **{golden_pancakes}**
        
        <:any:{pancake_data['???']['icon']}> **???** - ({icons.wool()}{pancake_data['???']['cost']})
        {pancake_data['???']['description']} - Owned: **{glitched_pancakes}**

        ⚪ - Cannot afford
        
        {icons.wool()}**{wool}**
        '''

        buttons = [
            Button(
                style=ButtonStyle.PRIMARY,
                label='Buy',
                custom_id='buy_pancakes_1',
                emoji= PartialEmoji(id=1147281411854839829, name='Pancake')
            ),
            Button(
                style=ButtonStyle.PRIMARY,
                label='Buy',
                custom_id='buy_pancakes_golden',
                emoji= PartialEmoji(id=1152330988022681821, name='Golden Pancake')
            ),
            Button(
                style=ButtonStyle.PRIMARY,
                label='Buy',
                custom_id='buy_pancakes_glitched',
                emoji= PartialEmoji(id=1152356972423819436, name='???')
            ),
            Button(
                style=ButtonStyle.RED,
                label='Go Back',
                custom_id='go_back'
            )
        ]

        for i, button in enumerate(buttons):
            if i == 0:
                if wool < 200:
                    button.disabled = True
                    button.style = ButtonStyle.GREY
                else:
                    button.disabled = False
                    button.style = ButtonStyle.PRIMARY
            if i == 1:
                if wool < 10_000:
                    button.disabled = True
                    button.style = ButtonStyle.GREY
                else:
                    button.disabled = False
                    button.style = ButtonStyle.PRIMARY
            if i == 2:
                if wool < 999_999:
                    button.disabled = True
                    button.style = ButtonStyle.GREY
                else:
                    button.disabled = False
                    button.style = ButtonStyle.PRIMARY

        return embed, buttons

    async def open_backgrounds_json(self):
        async with aiofiles.open('Data/backgrounds.json', 'r') as f:
            strdata = await f.read()

        return json.loads(strdata)

    async def open_backgrounds(self, uid: int, page: int):

        wool = database.fetch('user_data', 'wool', uid)

        embed = self.buy_background_embed
        buttons = self.get_background_buttons()

        current_background = self.current_background_stock[page]

        try:
            description = current_background['description']
        except KeyError:
            description = ''

        embed.description = f'''
        **{current_background['name']}** - ({icons.wool()}{current_background['cost']})
        {description}
        
        🔴 - Already owned
        ⚪ - Can't afford
        '''

        all_backgrounds = await self.open_backgrounds_json()
        backgrounds = self.current_background_stock
        owned_background_ids = database.fetch('user_data', 'unlocked_backgrounds', uid)
        owned_backgrounds = []

        for i in range(len(owned_background_ids)):
            owned_backgrounds.append(all_backgrounds['background'][owned_background_ids[i]])

        if backgrounds[page] in owned_backgrounds:

            bg = backgrounds[page]

            buttons[1].disabled = False
            buttons[1].style = ButtonStyle.PRIMARY

            if wool < bg['cost']:
                buttons[1].disabled = True
                buttons[1].style = ButtonStyle.GREY

            if bg in owned_backgrounds:
                buttons[1].disabled = True
                buttons[1].style = ButtonStyle.RED

        embed.set_image(url=current_background['image'])

        return embed, buttons

    async def open_treasures(self, uid: int):

        wool = database.fetch('user_data', 'wool', uid)

        percentage_difference = ((self.current_stock_price - 1) / 1) * 100

        # Determine whether the price has increased or decreased
        if self.current_stock_price > 1:
            price_change_symbol = '+'
        elif self.current_stock_price < 1:
            price_change_symbol = '-'
        else:
            price_change_symbol = ''

        get_treasures = self.get_treasures()

        treasures = []

        for treasure_id in self.current_treasure_stock:
            treasure = get_treasures[treasure_id]
            adjusted_price = int(treasure['price'] * self.current_stock_price)
            description = f"<:any:{treasure['emoji']}> **{treasure['name']}** - (**{icons.wool()}{adjusted_price}** *was {icons.wool()}{treasure['price']}*)\n{treasure['description']}"

            treasures.append({
                'object': treasure,
                'description': description,
                'price': adjusted_price
            })

        descriptions = '\n\n'.join([treasure['description'] for treasure in treasures])

        buttons = self.get_treasure_buttons()
        embed = Embed(
            title='Buy Treasures',
            color=0x8b00cc,
            description=f'''
            Well well well, it seems you're interested in my personal wares! These are all treasures I found through willing traders.
            
            If you have any treasures yourself, I'm more than happy to trade wool for your finds!
            
            **Current Stock Price:** {price_change_symbol}{abs(int(percentage_difference))}% difference.
            
            {descriptions}
            
            ⚪ - Cannot afford
            
            {icons.wool()}**{wool}**
            '''
        )

        embed.set_thumbnail('https://cdn.discordapp.com/attachments/1040653069794410567/1106652038772830238/Magpie.webp')

        for i, treasure in enumerate(treasures):
            buttons[i].label = 'Buy'
            buttons[i].style = ButtonStyle.PRIMARY
            buttons[i].emoji = PartialEmoji(id=treasure['object']['emoji'])

            if wool < treasure['price']:
                buttons[i].disabled = True
                buttons[i].style = ButtonStyle.GREY

        return embed, buttons

    async def open_sell_treasures(self, uid: int):

        wool = database.fetch('user_data', 'wool', uid)
        user_treasures = database.fetch('nikogotchi_data', 'treasure', uid)

        percentage_difference = ((self.current_stock_price - 1) / 1) * 100

        # Determine whether the price has increased or decreased
        if self.current_stock_price > 1:
            price_change_symbol = '+'
        elif self.current_stock_price < 1:
            price_change_symbol = '-'
        else:
            price_change_symbol = ''

        treasures = self.get_treasures()

        options = []

        for i, item in enumerate(treasures):
            if user_treasures[i] > 0:
                options.append(
                    StringSelectOption(
                        label=f'{item["name"]} - {int(item["price"] * self.current_stock_price)} wool (x{user_treasures[i]})',
                        value=str(i),
                        emoji=PartialEmoji(id=item['emoji'])
                    )
                )

        no_sellable_items = False

        if len(options) == 0:
            no_sellable_items = True
            options.append(
                StringSelectOption(
                    label='No Treasures',
                    value='-1'
                )
            )

        embed = Embed(
            title='Sell Treasures',
            color=0x8b00cc,
            description=f'''
            Ooh, what kind of treasures do you have? I'm more than happy to trade wool for your finds!
            
            **Current Stock Price:** {self.current_stock_price} ({price_change_symbol}{abs(int(percentage_difference))}% difference.)
            
            {icons.wool()}**{wool}**
            '''
        )

        embed.set_thumbnail('https://cdn.discordapp.com/attachments/1040653069794410567/1106652038772830238/Magpie.webp')

        if not no_sellable_items:
            select = StringSelectMenu(
                *options,
                placeholder='Select a treasure to sell.',
                custom_id='sell_treasures_menu'
            )
        else:
            select = StringSelectMenu(
                *options,
                placeholder='No Treasures',
                custom_id='sell_treasures_menu',
                disabled=True
            )

        buttons = [
            Button(
                style=ButtonStyle.PRIMARY,
                label='Buy Treasures',
                custom_id='shop_treasures'
            )
        ]

        components = spread_to_rows(select, *buttons)

        return embed, components
