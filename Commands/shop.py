from datetime import datetime, timedelta

from interactions import *
from interactions.api.events import Component
from Utilities.fancysend import *
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
            available_treasures = self.get_treasures()

            for _ in range(3):
                treasure_stocks.append(random.randint(0, len(available_treasures) - 1))

            stock_modifier = round(random.uniform(0.5, 1.5), 1)

            self.current_background_stock = [background_1, background_2, background_3]
            self.current_treasure_stock = treasure_stocks
            self.current_stock_price = stock_modifier

            new_time = datetime.now() + timedelta(days=1)

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

    @component_callback('buy_blue', 'buy_green', 'buy_red', 'buy_yellow')
    async def buy_capsules_callback(self, ctx: ComponentContext):

        wool = await database.get('user_data', ctx.author.id, 'wool')

        badges = await badge_manager.open_badges()
        badges = badges['shop']

        custom_id = ctx.custom_id

        footer = ''

        if custom_id == 'buy_blue':
            if wool < badges[0]['requirement']:
                footer = '[ Not enough wool. ]'
            else:
                await database.set('user_data', 'wool', ctx.author.id, wool - badges[0]['requirement'])
                await database.set('nikogotchi_data', 'nikogotchi_status', ctx.author.id, 1)
                await database.set('nikogotchi_data', 'rarity', ctx.author.id, 0)
                footer = '[ Successfully bought a Blue Capsule! ]'

        if custom_id == 'buy_green':
            if wool < badges[1]['requirement']:
                footer = '[ Not enough wool. ]'
            else:
                await database.set('user_data', 'wool', ctx.author.id, wool - badges[1]['requirement'])
                await database.set('nikogotchi_data', 'nikogotchi_status', ctx.author.id, 1)
                await database.set('nikogotchi_data', 'rarity', ctx.author.id, 1)
                footer = '[ Successfully bought a Green Capsule! ]'

        if custom_id == 'buy_red':
            if wool < badges[2]['requirement']:
                footer = '[ Not enough wool. ]'
            else:
                await database.set('user_data', 'wool', ctx.author.id, wool - badges[2]['requirement'])
                await database.set('nikogotchi_data', 'nikogotchi_status', ctx.author.id, 1)
                await database.set('nikogotchi_data', 'rarity', ctx.author.id, 2)
                footer = '[ Successfully bought a Red Capsule! ]'

        if custom_id == 'buy_yellow':
            if wool < badges[3]['requirement']:
                footer = '[ Not enough wool. ]'
            else:
                await database.set('user_data', 'wool', ctx.author.id, wool - badges[3]['requirement'])
                await database.set('nikogotchi_data', 'nikogotchi_status', ctx.author.id, 1)
                await database.set('nikogotchi_data', 'rarity', ctx.author.id, 3)
                footer = '[ Successfully bought a Yellow Capsule! ]'

        embed, buttons = await self.get_capsules(int(ctx.author.id))

        embed.set_footer(text=footer)

        await ctx.edit_origin(embed=embed, components=buttons)

    @component_callback('buy_pancakes_1', 'buy_pancakes_10', 'buy_pancakes_50')
    async def buy_pancakes_callback(self, ctx: ComponentContext):

        await ctx.defer(edit_origin=True)

        wool = await database.get('user_data', ctx.author.id, 'wool')
        pancakes = await database.get('nikogotchi_data', ctx.author.id, 'pancakes')
        custom_id = ctx.custom_id

        footer = ''

        if custom_id == 'buy_pancakes_1':
            if wool < 150:
                footer = '[ You do not have enough wool to buy a pancake! ]'
            else:
                await database.set('user_data', 'wool', ctx.author.id, wool - 150)
                await database.set('nikogotchi_data', 'pancakes', ctx.author.id, pancakes + 1)
                footer = f'[ Successfully bought a pancake! ]'

        if custom_id == 'buy_pancakes_10':
            if wool < 300:
                footer = '[ You do not have enough wool to buy 10 pancakes! ]'
            else:
                await database.set('user_data', 'wool', ctx.author.id, wool - 1000)
                await database.set('nikogotchi_data', 'pancakes', ctx.author.id, pancakes + 10)
                footer = f'[ Successfully bought 10 pancakes! ]'

        if custom_id == 'buy_pancakes_50':
            if wool < 500:
                footer = '[ You do not have enough wool to buy 50 pancakes! ]'
            else:
                await database.set('user_data', 'wool', ctx.author.id, wool - 5000)
                await database.set('nikogotchi_data', 'pancakes', ctx.author.id, pancakes + 50)
                footer = f'[ Successfully bought 50 pancakes! ]'

        embed, buttons = await self.get_pancakes(int(ctx.author.id))

        embed.set_footer(text=footer)

        await ctx.edit_origin(embed=embed, components=buttons)

    @component_callback('go_back')
    async def go_back(self, ctx: ComponentContext):
        embed, buttons = await self.get_main_shop(int(ctx.author.id))
        await ctx.edit_origin(embed=embed, components=buttons)

    async def get_main_shop(self, uid: int):

        embed = self.main_shop_embed
        embed.description = f'''
        **Welcome to the shop!**
        
        Here you can exchange your {icons.wool()}Wool for some colorful and shiny backgrounds, capsules and more! You can even sell any sparkly treasures you find here too!
        
        Feel free to browse through the categories by clicking on one of the buttons, or simply exit the shop by dismissing this message.
        As a seasoned merchant and purveyor of fine goods, I can assure you that my stock is always worth checking out.

        {icons.wool()}**{await database.get('user_data', uid, 'wool')}**
        '''

        embed.set_thumbnail('https://cdn.discordapp.com/attachments/1040653069794410567/1106652038772830238/Magpie.webp')
        buttons = self.get_shop_buttons()

        return embed, buttons

    async def get_capsules(self, uid: int):

        wool = await database.get('user_data', uid, 'wool')
        badges = await badge_manager.open_badges()
        badges = badges['shop']

        embed = self.buy_capsules_embed
        buttons = self.get_capsules_buttons()

        embed.thumbnail = 'https://cdn.discordapp.com/attachments/1040653069794410567/1106652038772830238/Magpie.webp'

        embed.description = f'''
        Want a companion for your journey? Now you can by buying one of these capsules! By purchasing one, you can unlock a random **Nikogotchi** to take care of! The rarer the capsule, the cooler the Nikogotchi!
        
        After purchasing a Nikogotchi, run the ``/nikogotchi check`` command to see your new friend! Make sure to take care of them, as if any of their needs are not met, they will lose health and die...
        
        By feeding them using pancakes, giving them attention and cleaning them, your Nikogotchi will live for a very long time! Cleaning them and giving them attention is easy enough, but you'll need to buy pancakes from me!
        
        Just keep in mind that you can only have one Nikogotchi at a time. The only way to get another one is to  send away your current one or if it has passed away.
        
        <:any:1147279938660089898> **Blue Capsule** - Teeming with blue phosphor, this capsule will give you a *common* Nikogotchi. ({icons.wool()}10000)
        
        <:any:1147279943387070494> **Green Capsule** - Teeming with green phosphor, this capsule will give you a *uncommon* Nikogotchi. ({icons.wool()}50000)
        
        <:any:1147280712328810536> **Red Capsule** - Teeming with red phosphor, this capsule will give you a *rare* Nikogotchi. ({icons.wool()}100000)
        
        <:any:1147279947086438431> **Yellow Capsule** - Teeming with yellow phosphor, this capsule will give you an ***extra rare*** Nikogotchi. ({icons.wool()}500000)
        
        ⚪ - Cannot afford
        🔴 - Already owned
        
        {icons.wool()}**{wool}**
        '''

        for i, badge in enumerate(badges):
            if badge['requirement'] > wool:
                buttons[i].disabled = True
                buttons[i].style = ButtonStyle.GREY
            elif await database.get('nikogotchi_data', uid, 'nikogotchi_status') >= 1:
                buttons[i].disabled = True
                buttons[i].style = ButtonStyle.DANGER
            else:
                buttons[i].disabled = False
                buttons[i].style = ButtonStyle.PRIMARY

        return embed, buttons

    async def get_pancakes(self, uid: int):

        wool = await database.get('user_data', uid, 'wool')
        pancakes = await database.get('nikogotchi_data', uid, 'pancakes')

        embed = Embed(
            title='Buy Pancakes',
            color=0x8b00cc
        )

        embed.set_thumbnail('https://cdn.discordapp.com/attachments/1040653069794410567/1106652038772830238/Magpie.webp')
        embed.description = f'''
        Use these pancakes to feed your Nikogotchi!
        
        1x Pancake - {icons.wool()}150
        10x Pancakes - {icons.wool()}1000
        50x Pancakes - {icons.wool()}5000

        ⚪ - Cannot afford
        
        {icons.wool()}**{wool}**
        <:any:1147281411854839829> **{pancakes}**
        '''

        buttons = [
            Button(
                style=ButtonStyle.PRIMARY,
                label='Buy 1x',
                custom_id='buy_pancakes_1'
            ),
            Button(
                style=ButtonStyle.PRIMARY,
                label='Buy 10x',
                custom_id='buy_pancakes_10'
            ),
            Button(
                style=ButtonStyle.PRIMARY,
                label='Buy 50x',
                custom_id='buy_pancakes_50'
            ),
            Button(
                style=ButtonStyle.RED,
                label='Go Back',
                custom_id='go_back'
            )
        ]

        for i, button in enumerate(buttons):
            if i == 0:
                if wool < 150:
                    button.disabled = True
                    button.style = ButtonStyle.GREY
                else:
                    button.disabled = False
                    button.style = ButtonStyle.PRIMARY
            if i == 1:
                if wool < 1000:
                    button.disabled = True
                    button.style = ButtonStyle.GREY
                else:
                    button.disabled = False
                    button.style = ButtonStyle.PRIMARY
            if i == 2:
                if wool < 5000:
                    button.disabled = True
                    button.style = ButtonStyle.GREY
                else:
                    button.disabled = False
                    button.style = ButtonStyle.PRIMARY

        return embed, buttons

    pages = [{"uid": 0, "page": 0}]

    async def open_backgrounds(self, uid: int, page: int):

        wool = await database.get('user_data', uid, 'wool')

        embed = self.buy_background_embed
        buttons = self.get_background_buttons()

        current_background = self.current_background_stock[page]

        embed.description = f'''
        **{current_background['name']}**
        
        Will you buy this background for {icons.wool()}{current_background['cost']}?
        
        🔴 - Already owned
        ⚪ - Can't afford
        '''

        backgrounds = self.current_background_stock
        owned_backgrounds = await database.get('user_data', uid, 'unlocked_backgrounds')

        for i, bg in enumerate(backgrounds):

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

        wool = await database.get('user_data', uid, 'wool')

        percentage_difference = ((self.current_stock_price - 1) / 1) * 100

        # Determine whether the price has increased or decreased
        if self.current_stock_price > 1:
            price_change_symbol = '+'
        elif self.current_stock_price < 1:
            price_change_symbol = '-'
        else:
            price_change_symbol = ''

        get_treasures = self.get_treasures()

        first_treasure = get_treasures[self.current_treasure_stock[0]]
        second_treasure = get_treasures[self.current_treasure_stock[1]]
        third_treasure = get_treasures[self.current_treasure_stock[2]]

        first_treasure_adjusted_price = int(first_treasure['price'] * self.current_stock_price)
        second_treasure_adjusted_price = int(second_treasure['price'] * self.current_stock_price)
        third_treasure_adjusted_price = int(third_treasure['price'] * self.current_stock_price)
        buttons = self.get_treasure_buttons()
        embed = Embed(
            title='Buy Treasures',
            color=0x8b00cc,
            description=f'''
            Well well well, it seems you're interested in my personal wares! These are all treasures I found through willing traders.
            
            If you have any treasures yourself, I'm more than happy to trade wool for your finds!
            
            
            **Current Stock Price:** {self.current_stock_price} ({price_change_symbol}{abs(int(percentage_difference))}% difference.)
            
            <:any:{first_treasure['emoji']}> **{first_treasure['name']}** - *{icons.wool()}{first_treasure['price']}* > **{icons.wool()}{first_treasure_adjusted_price}**
            
            <:any:{second_treasure['emoji']}> **{second_treasure['name']}** - *{icons.wool()}{second_treasure['price']}* > **{icons.wool()}{second_treasure_adjusted_price}**
            
            <:any:{third_treasure['emoji']}> **{third_treasure['name']}** - *{icons.wool()}{third_treasure['price']}* > **{icons.wool()}{third_treasure_adjusted_price}**
            
            
            ⚪ - Cannot afford
            
            {icons.wool()}**{wool}**
            '''
        )

        embed.set_thumbnail('https://cdn.discordapp.com/attachments/1040653069794410567/1106652038772830238/Magpie.webp')

        buttons[0].emoji = PartialEmoji(id=first_treasure['emoji'])
        buttons[1].emoji = PartialEmoji(id=second_treasure['emoji'])
        buttons[2].emoji = PartialEmoji(id=third_treasure['emoji'])

        if wool < first_treasure_adjusted_price:
            buttons[0].disabled = True
            buttons[0].style = ButtonStyle.GREY

        if wool < second_treasure_adjusted_price:
            buttons[1].disabled = True
            buttons[1].style = ButtonStyle.GREY

        if wool < third_treasure_adjusted_price:
            buttons[2].disabled = True
            buttons[2].style = ButtonStyle.GREY

        return embed, buttons

    async def open_sell_treasures(self, uid: int):

        wool = await database.get('user_data', uid, 'wool')
        user_treasures = await database.get('nikogotchi_data', uid, 'treasure')

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


    @component_callback('move_left', 'move_right', 'buy_background')
    async def background_callbacks(self, ctx: ComponentContext):

        custom_id = ctx.custom_id

        i = 0
        for page in self.pages:
            if page['uid'] == str(ctx.author.id):
                break

            i += 1

        if i == len(self.pages):
            self.pages.append({'uid': str(ctx.author.id), 'page': 0})
            current_page = self.pages[-1]
            i = self.pages.index(current_page)
        else:
            current_page = self.pages[i]

        if custom_id == 'move_left':

            if current_page['page'] <= 0:
                current_page['page'] = 2
            else:
                current_page['page'] -= 1

        if custom_id == 'move_right':

            if current_page['page'] >= 2:
                current_page['page'] = 0
            else:
                current_page['page'] += 1

        embed, buttons = await self.open_backgrounds(int(ctx.author.id), current_page['page'])

        footer = ''

        if custom_id == 'buy_background':
            background = self.current_background_stock[current_page['page']]
            wool = await database.get('user_data', ctx.author.id, 'wool')

            if wool < background['cost']:
                footer = "[ You don't have enough wool for this! ]"
            else:
                all_backgrounds = await self.get_backgrounds()

                unlocked_background = await database.get('user_data', ctx.author.id, 'unlocked_backgrounds')

                background_index = 0

                for i, bg in enumerate(all_backgrounds):
                    if bg['name'] == background['name']:
                        unlocked_background.append(background_index)
                        break

                    background_index += 1

                await database.set('user_data', 'wool', ctx.author.id, wool - background['cost'])
                await database.set('user_data', 'unlocked_backgrounds', ctx.author.id, unlocked_background)

                embed.set_footer(f'[ Successfully bought {background["name"]}! ]')

        embed, buttons = await self.open_backgrounds(int(ctx.author.id), current_page['page'])

        embed.set_footer(footer)

        await ctx.edit_origin(embed=embed, components=buttons)

    @component_callback('buy_treasure_1', 'buy_treasure_2', 'buy_treasure_3', 'sell_treasures')
    async def treasure_callbacks(self, ctx: ComponentContext):

        custom_id = ctx.custom_id

        embed, components = await self.open_treasures(ctx.author.id)

        wool = await database.get('user_data', ctx.author.id, 'wool')
        user_treasures = await database.get('nikogotchi_data', ctx.author.id, 'treasure')
        get_treasures = self.get_treasures()

        footer = ''

        treasure_1_price = get_treasures[self.current_treasure_stock[0]]['price'] * self.current_stock_price
        treasure_2_price = get_treasures[self.current_treasure_stock[1]]['price'] * self.current_stock_price
        treasure_3_price = get_treasures[self.current_treasure_stock[2]]['price'] * self.current_stock_price

        if custom_id == 'buy_treasure_1':
            if wool < treasure_1_price:
                footer = "[ You don't have enough wool for this! ]"
            else:
                user_treasures[self.current_treasure_stock[0]] += 1
                await database.set('nikogotchi_data', 'treasure', ctx.author.id, user_treasures)
                await database.set('user_data', 'wool', ctx.author.id, wool - treasure_1_price)
                footer = f'[ Successfully bought {get_treasures[self.current_treasure_stock[0]]["name"]}! ]'

        if custom_id == 'buy_treasure_2':
            if wool < treasure_2_price:
                footer = "[ You don't have enough wool for this! ]"
            else:
                user_treasures[self.current_treasure_stock[1]] += 1
                await database.set('nikogotchi_data', 'treasure', ctx.author.id, user_treasures)
                await database.set('user_data', 'wool', ctx.author.id, wool - treasure_2_price)
                footer = f'[ Successfully bought {get_treasures[self.current_treasure_stock[1]]["name"]}! ]'

        if custom_id == 'buy_treasure_3':
            if wool < treasure_3_price:
                footer = "[ You don't have enough wool for this! ]"
            else:
                user_treasures[self.current_treasure_stock[2]] += 1
                await database.set('nikogotchi_data', 'treasure', ctx.author.id, user_treasures)
                await database.set('user_data', 'wool', ctx.author.id, wool - treasure_3_price)
                footer = f'[ Successfully bought {get_treasures[self.current_treasure_stock[2]]["name"]}! ]'

        if custom_id != 'sell_treasures':
            embed, components = await self.open_treasures(ctx.author.id)
        else:
            embed, components = await self.open_sell_treasures(ctx.author.id)

        embed.set_footer(text=footer)

        await ctx.edit_origin(embed=embed, components=components)

    @component_callback('sell_treasures_menu')
    async def sell_treasures_menu(self, ctx: ComponentContext):

        value = int(ctx.values[0])

        wool = await database.get('user_data', ctx.author.id, 'wool')
        user_treasures = await database.get('nikogotchi_data', ctx.author.id, 'treasure')
        get_treasures = self.get_treasures()

        footer = ''

        if user_treasures[value] == 0:
            footer = "[ You don't have any treasures to sell! ]"
        else:
            user_treasures[value] -= 1
            await database.set('nikogotchi_data', 'treasure', ctx.author.id, user_treasures)
            await database.set('user_data', 'wool', ctx.author.id, wool + get_treasures[value]['price'] * self.current_stock_price)

            footer = f'[ Successfully sold {get_treasures[value]["name"]}! ]'

        embed, components = await self.open_sell_treasures(ctx.author.id)

        embed.set_footer(text=footer)

        await ctx.edit_origin(embed=embed, components=components)
