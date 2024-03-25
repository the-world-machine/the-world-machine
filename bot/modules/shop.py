from dataclasses import asdict
import random
from interactions import *
from utilities.shop.fetch_items import fetch_background, fetch_item, fetch_treasure
from utilities.fancy_send import *
from utilities.bot_icons import *
from utilities.shop.fetch_shop_data import DictItem, Item, ShopData, fetch_shop_data, reset_shop_data
from datetime import datetime, timedelta
from database import NikogotchiData, UserData
from localization.loc import Localization, fnum
import re

class Shop(Extension):
    
    daily_shop: ShopData = None
    
    async def load_shop(self, loc: str):
        
        if self.daily_shop is not None:
            return
        
        data = await fetch_shop_data()
        
        old_time = data.last_reset_date
        now = datetime.now()
        
        should_reset = now > old_time + timedelta(days=1)
        
        if should_reset:
            data = await reset_shop_data(loc)
        
        self.daily_shop = data

    @component_callback('select_treasure_sell')
    async def select_treasure_sell_callback(self, ctx: ComponentContext):
         
        await ctx.defer(edit_origin=True)
        
        await self.load_shop(ctx.guild_locale)
        
        treasure = ctx.values[0]
        
        embed, components = await self.embed_manager(ctx, 'Sell_Treasures', selected_treasure=treasure)
        
        await ctx.edit(embed=embed, components=components)
        
    @component_callback('select_treasure')
    async def select_treasure_callback(self, ctx: ComponentContext):
         
        await ctx.defer(edit_origin=True)
        
        await self.load_shop(ctx.guild_id)
        
        treasure = ctx.values[0]
        
        embed, components = await self.embed_manager(ctx, 'Treasures', selected_treasure=treasure)
        
        await ctx.edit(embed=embed, components=components)

    @component_callback('sell_treasure_menu')
    async def sell_treasure_callback(self, ctx: ComponentContext):
        
        await ctx.defer(edit_origin=True)
        
        await self.load_shop(ctx.guild_id)
        
        embed, components = await self.embed_manager(ctx, 'Sell_Treasures', selected_treasure=None)
        
        await ctx.edit(embed=embed, components=components)
        
    r_treasure_sell = re.compile(r'treasure_sell_(.*)_(.*)')
    @component_callback(r_treasure_sell)
    async def treasure_sell_action_callback(self, ctx: ComponentContext):
        
        await ctx.defer(edit_origin=True)
        
        localization = Localization(ctx.guild_locale)
        
        await self.load_shop(ctx.guild_id)
        
        match = self.r_treasure_sell.search(ctx.custom_id)
        
        if not match:
            return
        
        treasure_id = match.group(1)
        amount_to_sell = match.group(2)
        
        stock_price = self.daily_shop.stock_price
        
        user_data: UserData = await UserData(ctx.author.id).fetch()
        
        all_treasures = await fetch_treasure()
        owned_treasure = user_data.owned_treasures
        
        amount_of_treasure = owned_treasure[treasure_id]
        
        treasure = DictItem(nid=treasure_id, **all_treasures[treasure_id], type=0)
        
        result_text = ''
        
        treasure_loc: dict = localization.l(f'items.treasures.{treasure_id}')
        
        async def update():
            
            if amount_to_sell == 'all':
                embed, components = await self.embed_manager(ctx, 'Sell_Treasures', selected_treasure=treasure_id)
            else:
                embed, components = await self.embed_manager(ctx, 'Sell_Treasures', selected_treasure=treasure_id)
            
            embed.set_footer(result_text)
            
            await ctx.edit(embed=embed, components=components)
            
        if amount_of_treasure <= 0:
            result_text = localization.l('shop.traded_fail')
            await update()
            return
            
        sell_price = 0
            
        if amount_to_sell == 'all':
            amount = amount_of_treasure
            
            sell_price = int(amount_of_treasure * treasure.cost * stock_price)
            owned_treasure[treasure_id] = 0
        else:
            amount = 1
            
            sell_price = int(treasure.cost * stock_price)
            owned_treasure[treasure_id] -= 1
            
        result_text = localization.l('shop.traded_sell', item_name=treasure_loc['name'], amount=amount, price=sell_price)
            
        await user_data.update(
            owned_treasures=owned_treasure,
            wool=user_data.wool + sell_price
        )
        
        await update()
        
    r_treasure_buy = re.compile(r'treasure_buy_(.*)_(.*)')
    @component_callback(r_treasure_buy)
    async def buy_treasure_callback(self, ctx: ComponentContext):
        
        await ctx.defer(edit_origin=True)
        
        localization = Localization(ctx.guild_locale)
        
        await self.load_shop(ctx.guild_id)
        
        user_data: UserData = await UserData(ctx.author.id).fetch()
        
        match = self.r_treasure_buy.match(ctx.custom_id)
        
        if not match:
            return
        
        treasure_id = match.group(1)
        amount_to_buy = match.group(2)
        
        all_treasures = await fetch_treasure()
        
        treasure = DictItem(nid=treasure_id, **all_treasures[treasure_id], type=0)
        
        result_text = ''
        
        treasure_price = treasure.cost * self.daily_shop.stock_price
        
        async def update(text: str):
            embed, components = await self.embed_manager(ctx, 'Treasures', selected_treasure=treasure_id)
            embed.set_footer(text)
            
            await ctx.edit(embed=embed, components=components)
        
        if user_data.wool < treasure_price:
            return await update(localization.l('shop.traded_fail'))

        current_balance = user_data.wool
        price = 0
        amount = 0
        
        treasure_loc: dict = localization.l(f'items.treasures.{treasure.nid}')
        
        name = treasure_loc['name']
        
        if amount_to_buy == 'All':
            while True:
                current_balance -= treasure_price
                
                if current_balance <= 0:
                    break
                
                price += int(treasure_price)
                amount += 1
        else:
            price = int(treasure_price)
            amount = 1
        
        owned_treasure = user_data.owned_treasures
        
        owned_treasure[treasure_id] = owned_treasure.get(treasure_id, 0) + amount
        
        await user_data.update(
            wool=user_data.wool - price,
            owned_treasures=owned_treasure
        )
        
        return await update(localization.l('shop.traded', item_name=name, amount=amount, price=price))
        
    r_buy_bg = re.compile(r'buy_bg_(.*)_(\d+)')
    @component_callback(r_buy_bg)
    async def buy_bg_callback(self, ctx: ComponentContext):
        
        await ctx.defer(edit_origin=True)
        
        localization = Localization(ctx.guild_locale)
        
        user: UserData = await UserData(ctx.author.id).fetch()
        
        match = self.r_buy_bg.match(ctx.custom_id)
        
        if not match:
            return
        
        bg_id = match.group(1)
        page = int(match.group(2))
        
        bg_data = await fetch_background()
        bg = DictItem(nid=bg_id, **bg_data)
        
        owned_backgrounds = user.owned_backgrounds
        
        async def update(text: str):
            embed, components = await self.embed_manager(ctx, 'Backgrounds', page=page)
            embed.set_footer(text)
            
            await ctx.send(embed=embed, components=components, ephemeral=True)
        
        if bg.nid in owned_backgrounds:
            return await update(localization.l('shop.traded_fail'))
        
        if user.wool < bg.cost:
            return await update(localization.l('shop.traded_fail'))
        
        owned_backgrounds.append(bg.nid)
        
        await user.update(
            owned_backgrounds=owned_backgrounds,
            wool=user.wool - bg.cost
        )
        
        await update(localization.l('shop.traded_fail'))

    @component_callback('nikogotchi_buy')
    async def buy_nikogotchi_callback(self, ctx: ComponentContext):
        
        await ctx.defer(edit_origin=True)
        
        localization = Localization(ctx.guild_locale)
        
        user_data: UserData = await UserData(ctx.author.id).fetch()
        nikogotchi: NikogotchiData = await NikogotchiData(ctx.author.id).fetch()
        
        capsule_id = random.randint(0, 3)
        
        capsules = await fetch_item()
        capsules = capsules['capsules']
        
        nikogotchi_capsule = Item(**capsules[capsule_id])
        capsule_loc = localization.l(f'items.capsules.{nikogotchi_capsule.id}')
        
        async def update(result: str):
            embed, components = await self.embed_manager(ctx, 'capsules')
            embed.set_footer(result)
            
            await ctx.edit(embed=embed, components=components)
        
        if nikogotchi.data or nikogotchi.nikogotchi_available:
            return await update(localization.l('shop.traded_fail'))
        
        if user_data.wool < nikogotchi_capsule.cost:
            return await update(localization.l('shop.traded_fail'))
        
        await nikogotchi.update(nikogotchi_available=True, rarity=capsule_id)
        await user_data.update(wool=user_data.wool - nikogotchi_capsule.cost)
        
        await update(localization.l('shop.nikogotchi.result', amount=nikogotchi_capsule.cost, capsule_name=capsule_loc))
        
    r_buy_object = re.compile(r'buy_([^\d]+)_(\d+)')
    @component_callback(r_buy_object)
    async def buy_pancakes_callback(self, ctx: ComponentContext):
        
        await ctx.defer(edit_origin=True)
        
        localization = Localization(ctx.guild_locale)
        
        user_data: UserData = await UserData(ctx.author.id).fetch()
        nikogotchi_data: NikogotchiData = await NikogotchiData(ctx.author.id).fetch()
        
        match = self.r_buy_object.match(ctx.custom_id)
        
        if not match:
            return
        
        item_category = match.group(1)
        item_id = int(match.group(2))
        
        result_text = ''
        
        async def update():
            
            embed, components = await self.embed_manager(ctx, item_category)
            
            embed.set_footer(result_text)
            
            return await ctx.edit(embed=embed, components=components)

        item = await fetch_item()
        item = item['pancakes'][item_id]
        item = Item(**item)
        
        item_loc: dict = localization.l(f'items.pancakes.{item.id}')
            
        if user_data.wool < item.cost:
            result_text = localization.l('shop.traded_fail')
            return await update()
        
        result_text = localization.l('shop.traded', price=item.cost, amount=1, item_icon=f'<:icon:{item.image}>', item_name=item_loc['name'])
        
        json_data = asdict(nikogotchi_data)
        
        await nikogotchi_data.update(**{item.id: json_data[item.id] + 1})
        
        await user_data.update(wool=user_data.wool - item.cost)
        await update()
        
        
    @component_callback('capsules', 'pancakes', 'Backgrounds', 'Treasures', 'go_back')
    async def main_shop_callbacks(self, ctx: ComponentContext):
        await ctx.defer(edit_origin=True)
        
        await self.load_shop(ctx.guild_id)
        
        embed, components = await self.embed_manager(ctx, ctx.custom_id, page=0)
            
        embed.color = 0x02f2c6
        
        await ctx.edit(embed=embed, components=components)
    
    
    r_page = re.compile(r'page_([^\d]+)_(\d+)')
    @component_callback(r_page)
    async def page_callback(self, ctx: ComponentContext):
        
        await self.load_shop(ctx.guild_id)
        
        await ctx.defer(edit_origin=True)
        
        match = self.r_page.match(ctx.custom_id)
        
        if not match:
            return
        
        action = match.group(1)
        bg_page = int(match.group(2))
        
        bgs = self.daily_shop.background_stock
        
        if action == 'prev':
            if bg_page > 0:
                bg_page -= 1
            else:
                bg_page = len(bgs) - 1
                
        if action == 'next':
            if bg_page < len(bgs) - 1:
                bg_page += 1
            else:
                bg_page = 0
                
        embed, components = await self.embed_manager(ctx, 'Backgrounds', page=bg_page)
        
        embed.color = 0x02f2c6
        
        await ctx.edit(embed=embed, components=components)
        
    ## EMBED MANAGER ---------------------------------------------------------------
    
    async def embed_manager(self, ctx: SlashContext, category: str, **kwargs):

        await self.load_shop(ctx.guild_id)
        
        localization = Localization(ctx.guild_locale)
        
        user_data: UserData = await UserData(ctx.author.id).fetch()
        
        wool: int = user_data.wool
        
        stock: str = localization.l('shop.stocks', value=self.daily_shop.stock_value, price=self.daily_shop.stock_price)
        
        user_wool = localization.l('shop.user_wool', wool=user_data.wool)
        magpie = EmbedAttachment('https://cdn.discordapp.com/attachments/1025158352549982299/1176956900928131143/Magpie.webp')
        
        go_back = Button(
            style=ButtonStyle.DANGER,
            custom_id='go_back',
            label=localization.l('shop.buttons.go_back')
        )
        
        b_trade: str = localization.l('shop.buttons.buy')
        b_owned: str = localization.l('shop.buttons.owned')
        b_poor: str = localization.l('shop.buttons.too_poor')
        
        if category == 'main_shop' or category == 'go_back':
            
            motds = localization.l('shop.motds')
            
            motd = motds[self.daily_shop.motd]
                
            title = localization.l('shop.main_title')
            description = localization.l('shop.main', motd=motd, user_wool=user_wool)
                
            embed = Embed(
                title=title,
                description=description,
                thumbnail=magpie
            )
            
            buttons = [
                    Button(
                        label=localization.l('shop.nikogotchi.title'),
                        emoji=PartialEmoji(id=1147279938660089898),
                        style=ButtonStyle.BLURPLE,
                        custom_id='capsules'
                    ),
                    
                    Button(
                        label=localization.l('shop.pancakes.title'),
                        emoji=PartialEmoji(id=1147281411854839829),
                        style=ButtonStyle.BLURPLE,
                        custom_id='pancakes'
                    ),
                    
                    Button(
                        label=localization.l('shop.backgrounds.title'),
                        emoji=PartialEmoji(id=1026181558392062032),
                        style=ButtonStyle.BLURPLE,
                        custom_id='Backgrounds'
                    ),
                    
                    Button(
                        label=localization.l('shop.treasures.title'),
                        emoji=PartialEmoji(id=1026135536190111755),
                        style=ButtonStyle.BLURPLE,
                        custom_id='Treasures'
                    )
                ]
            
            return embed, buttons
        
        elif category == 'capsules':
            
            nikogotchi: NikogotchiData = await NikogotchiData(ctx.author.id).fetch()
            capsules: dict = await fetch_item()
            cost = 50_000
            
            caspule_text = ''
            buttons = []
            
            for i, capsule in enumerate(capsules['capsules']):
                
                item = Item(**capsule)
                
                capsule_loc = localization.l(f'items.capsules.{item.id}')
                
            button = Button(
                label=b_trade,
                emoji=PartialEmoji(1147279947086438431),
                style=ButtonStyle.BLURPLE,
                custom_id=f'nikogotchi_buy'
            )
                
            if nikogotchi.nikogotchi_available or nikogotchi.data:
                button.disabled = True
                button.style = ButtonStyle.RED
                button.label = b_owned
            
            if wool < item.cost:
                button.disabled = True
                button.style = ButtonStyle.GRAY
                button.label = b_poor
                
            buttons.append(button)
                
            buttons.append(go_back)
                
            title = localization.l('shop.nikogotchi.title')
            description = localization.l('shop.nikogotchi.main', cost=cost, user_wool=user_wool)
            
            embed = Embed(
                title=title,
                description=description,
                thumbnail=magpie
            )
            
            return embed, buttons
        elif category == 'pancakes':
        
            pancake_data = await fetch_item()
            
            nikogotchi_data: NikogotchiData = await NikogotchiData(ctx.author.id).fetch()
            json_data = asdict(nikogotchi_data)
            
            pancake_text = ''
            buttons: list[Button] = []
            for id_, pancake in enumerate(pancake_data['pancakes']):
                
                pancake = Item(**pancake)
                
                owned = json_data[pancake.id]
                
                amount_owned = localization.l('shop.owned', amount=owned)
                pancake_loc: dict = localization.l(f'items.pancakes.{pancake.id}')
                
                pancake_text += f"<:pancake:{pancake.image}>  **{pancake_loc['name']}** - {icon_wool}{fnum(pancake.cost)} - {amount_owned}\n{pancake_loc['description']}\n"
                
                button = Button(
                    label=b_trade,
                    emoji=PartialEmoji(id=pancake.image),
                    style=ButtonStyle.BLURPLE,
                    custom_id=f'buy_pancakes_{id_}'
                )
                
                if wool < pancake.cost:
                    button.disabled = True
                    button.style = ButtonStyle.GRAY
                    button.label = b_poor
                
                buttons.append(button)
                
            buttons.append(go_back)
                
            title = localization.l('shop.pancakes.title')
            description = localization.l('shop.pancakes.main', items=pancake_text, user_wool=user_wool)
                
            embed = Embed(
                title=title,
                description=description,
                thumbnail=magpie
            )
            
            return embed, buttons
        
        elif category == 'Backgrounds':
            
            bg_page = kwargs['page']
            
            background: DictItem = self.daily_shop.background_stock[bg_page]
            user_backgrounds = user_data.owned_backgrounds
            
            background_name = localization.l(f'items.backgrounds.{background.nid}')
            background_description = localization.l('shop.backgrounds.main', bg_name=background_name, amount=background.cost, user_wool=user_wool)
            
            embed = Embed(
                title=background_name,
                description=background_description,
                thumbnail=magpie
            )
            
            embed.set_image(url=background.image)
            
            buttons = [
                Button(
                    label='<',
                    style=ButtonStyle.BLURPLE,
                    custom_id=f'page_prev_{bg_page}'
                ),
                Button(
                    label=b_trade,
                    style=ButtonStyle.GREEN,
                    custom_id=f'buy_bg_{background.nid}_{bg_page}'
                ),
                go_back,
                Button(
                    label='>',
                    style=ButtonStyle.BLURPLE,
                    custom_id=f'page_next_{bg_page}'
                )
            ]
            
            buy_button = buttons[1]
            
            if wool < background.cost:
                buy_button.disabled = True
                buy_button.style = ButtonStyle.GRAY
                buy_button.label = b_poor
            
            if background.nid in user_backgrounds:
                buy_button.disabled = True
                buy_button.style = ButtonStyle.RED
                buy_button.label = b_owned
                
            buttons[1] = buy_button
            
            return embed, buttons
            
        elif category == 'Treasures':
            
            selected_treasure = kwargs.get('selected_treasure', None)
            selected_treasure_loc = None
            buy_price_one = 0
            buy_price_all = 0
            
            treasure_details = localization.l('shop.treasures.treasure_not_selected')
            
            user_data = await UserData(ctx.author.id).fetch()
            
            owned = user_data.owned_treasures
            all_treasures = await fetch_treasure()
            
            if selected_treasure is not None:
                selected_treasure = DictItem(nid=selected_treasure, **all_treasures[selected_treasure], type=0)
                selected_treasure_loc: dict = localization.l(f'items.treasures.{selected_treasure.nid}')
                
                amount_selected = owned.get(selected_treasure.nid, 0)
                
                buy_price_one = int(selected_treasure.cost * self.daily_shop.stock_price)
                
                current_balance = user_data.wool
                
                amount = 0
                
                while True:
                    current_balance -= buy_price_one
                    
                    if current_balance <= 0:
                        break
                    
                    buy_price_all += int(buy_price_one)
                    amount += 1
                
                treasure_details = localization.l(
                    'shop.treasures.selected_treasure',
                    treasure_icon=f'<:treasure:{selected_treasure.image}>',
                    treasure_name=selected_treasure_loc['name'],
                    owned=localization.l('shop.owned', amount=amount_selected),
                    price_one=buy_price_one,
                    price_all=buy_price_all,
                    amount = amount
                )
            
            treasure_stock = self.daily_shop.treasure_stock

            buttons: list[Button] = []
            bottom_buttons: list[Button] = []
            
            user_data = await UserData(ctx.author.id).fetch()
            
            owned = user_data.owned_treasures

            treasure_list = []
            
            for treasure in treasure_stock:
                
                amount_owned = localization.l('shop.owned', amount=owned.get(treasure.nid, 0))
                treasure_loc: dict = localization.l(f'items.treasures.{treasure.nid}')
                
                treasure_list.append(
                    StringSelectOption(
                        label=localization.l('shop.treasures.option', name=treasure_loc['name'], price=treasure.cost),
                        description=treasure_loc['description'],
                        value=treasure.nid,
                        emoji=PartialEmoji(id=treasure.image)
                    )
                )
            
            if selected_treasure is not None:   
                button = Button(
                    label=b_trade,
                    emoji=PartialEmoji(id=selected_treasure.image),
                    style=ButtonStyle.BLURPLE,
                    custom_id=f'treasure_buy_{selected_treasure.nid}_One'
                )
                
                button_all = Button(
                    label=localization.l('shop.buttons.buy_all'),
                    emoji=PartialEmoji(id=selected_treasure.image),
                    style=ButtonStyle.BLURPLE,
                    custom_id=f'treasure_buy_{selected_treasure.nid}_All'
                )
                    
                if wool < buy_price_one:
                    button.disabled = True
                    button.style = ButtonStyle.GRAY
                    button.label = b_poor
                    
                    button_all.disabled = True
                    button_all.style = ButtonStyle.GRAY
                    button_all.label = b_poor
                    
                buttons.append(button)
                buttons.append(button_all)
            
            buttons.append(Button(
                label=localization.l('shop.treasures.sell_title'),
                style=ButtonStyle.GREEN,
                custom_id='sell_treasure_menu'
            ))
                
            buttons.append(go_back)
            
            
            title = localization.l('shop.treasures.title')
            description = localization.l('shop.treasures.buy_main', stock_market=stock, selected_treasure=treasure_details, user_wool=user_wool)
            
            embed = Embed(
                title=title,
                description=description,
                thumbnail=magpie
            )
            
            select_menu = None
            
            if len(treasure_list) > 0:
                select_menu = StringSelectMenu(
                    *treasure_list,
                    placeholder=localization.l('shop.treasures.placeholder'),
                    custom_id=f'select_treasure',
                )
            else:
                select_menu = StringSelectMenu(
                    '💥💥💥💥💥💥💥💥💥💥💥💥',
                    placeholder=localization.l('shop.treasures.cannot_sell'),
                    custom_id=f'select_treasure',
                    disabled=True
                )
            
            components = [ActionRow(select_menu), ActionRow(*buttons)]
                
            return embed, components
        
        elif category == 'Sell_Treasures':
            
            selected_treasure = kwargs['selected_treasure']
            selected_treasure_loc = None
            sell_price_one = 0
            sell_price_all = 0
            
            treasure_details = localization.l('shop.treasures.treasure_not_selected')
            
            user_data = await UserData(ctx.author.id).fetch()
            
            owned = user_data.owned_treasures
            all_treasures = await fetch_treasure()
            
            if selected_treasure is not None:
                selected_treasure = DictItem(nid=selected_treasure, **all_treasures[selected_treasure], type=0)
                selected_treasure_loc: dict = localization.l(f'items.treasures.{selected_treasure.nid}')
                
                sell_price_one = int(selected_treasure.cost * self.daily_shop.stock_price)
                sell_price_all = int(selected_treasure.cost * self.daily_shop.stock_price * owned[selected_treasure.nid])
                
                amount_selected = owned.get(selected_treasure.nid, 0)
                
                treasure_details = localization.l(
                    'shop.treasures.selected_treasure',
                    treasure_icon=f'<:treasure:{selected_treasure.image}>',
                    treasure_name=selected_treasure_loc['name'],
                    owned=localization.l('shop.owned', amount=amount_selected),
                    price_one=sell_price_one,
                    price_all=sell_price_all,
                    amount=amount_selected
                )
            
            treasure_selection = []
            
            for treasure_nid, amount in owned.items():
                
                if amount <= 0:
                    continue
                
                treasure = DictItem(nid=treasure_nid, **all_treasures[treasure_nid], type=0)
                
                treasure_loc = localization.l(f'items.treasures.{treasure_nid}')
                
                emoji=PartialEmoji(id=int(treasure.image))
                
                treasure_selection.append(
                    
                    StringSelectOption(
                        label=f'{treasure_loc["name"]} (x{amount})',
                        value=treasure_nid,
                        description=treasure_loc['description'],
                        emoji=emoji,
                    )
                )
                
            selection_description = ''
            
            buttons = []
            
            if selected_treasure is not None:
                treasure_id = selected_treasure.nid
                
                buttons = [
                    Button(
                        label=b_trade,
                        custom_id=f'treasure_sell_{treasure_id}_one',
                        style=ButtonStyle.GREEN
                    ),
                    Button(
                        label=localization.l('shop.buttons.buy_all'),
                        custom_id=f'treasure_sell_{treasure_id}_all',
                        style=ButtonStyle.GREEN
                    )
                ]
            else:
                treasure_id = 0
                
            buttons.append(go_back)    
                
            embed = Embed(
                title=localization.l('shop.treasures.sell_title'),
                description=localization.l(
                    'shop.treasures.sell_main',
                    stock_market=stock,
                    selected_treasure=treasure_details,
                   
                    user_wool=user_wool
                ),
                thumbnail=magpie
            )
            
            select_menu = None
            
            if len(treasure_selection) > 0:
                select_menu = StringSelectMenu(
                    *treasure_selection,
                    placeholder=localization.l('shop.treasures.placeholder'),
                    custom_id=f'select_treasure_sell',
                )
            else:
                select_menu = StringSelectMenu(
                    '💥💥💥💥💥💥💥💥💥💥💥💥',
                    placeholder=localization.l('shop.treasures.cannot_sell'),
                    custom_id=f'select_treasure_sell',
                    disabled=True
                )
            
            components = [ActionRow(select_menu), ActionRow(*buttons)]
                
            return embed, components
        
    @slash_command(description="Open the Shop!")
    async def shop(self, ctx: SlashContext):
        
        await ctx.defer(ephemeral=True)
        
        await self.load_shop(ctx.guild_locale)
        
        embed, button = await self.embed_manager(ctx, 'main_shop')
        embed.color = 0x02f2c6
        
        await ctx.send(embed=embed, components=button)