from dataclasses import asdict
from typing import Union
from interactions import *
from interactions.api.events import Component
from utilities.shop.fetch_items import fetch_background, fetch_item, fetch_treasure
from utilities.fancy_send import *
from utilities.bot_icons import *
from utilities.shop.fetch_shop_data import DictItem, Item, ShopData, fetch_shop_data, reset_shop_data
from datetime import datetime, timedelta
from database import NikogotchiData, UserData
from localization.loc import l, fnum
import re

class Shop(Extension):
    
    daily_shop: ShopData = None
    
    async def load_shop(self, guild_id: int):
        
        if self.daily_shop is not None:
            return
        
        data = await fetch_shop_data()
        
        old_time = data.last_reset_date
        now = datetime.now()
        
        should_reset = now > old_time + timedelta(days=1)
        
        if should_reset:
            data = await reset_shop_data(guild_id)
        
        self.daily_shop = data

    @component_callback('select_treasure')
    async def select_treasure_callback(self, ctx: ComponentContext):
         
        await ctx.defer(edit_origin=True)
        
        await self.load_shop(ctx.guild_id)
        
        treasure = ctx.values[0]
        
        embed, components = await self.embed_manager(ctx, 'Sell_Treasures', selected_treasure=treasure)
        
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
        
        await self.load_shop(ctx.guild_id)
        
        match = self.r_treasure_sell.search(ctx.component.custom_id)
        
        if not match:
            return
        
        treasure_id = match.group(1)
        amount_to_sell = match.group(2)
        
        stock_price = self.daily_shop.stock_price
        
        user_data = await UserData(ctx.author.id).fetch()
        
        all_treasures = await fetch_treasure()
        owned_treasure = user_data.owned_treasures
        
        amount_of_treasure = owned_treasure[treasure_id]
        
        treasure = DictItem(nid=treasure_id, **all_treasures[treasure_id], type=0)
        
        result_text = ''
        
        treasure_loc: dict = l(ctx.guild_locale, f'items.treasures.{treasure_id}')
        
        async def update():
            
            if amount_to_sell == 'all':
                embed, components = await self.embed_manager(ctx, 'Sell_Treasures', selected_treasure=None)
            else:
                embed, components = await self.embed_manager(ctx, 'Sell_Treasures', selected_treasure=treasure_id)
            
            embed.set_footer(result_text)
            
            await ctx.edit(embed=embed, components=components)
            
        if amount_of_treasure <= 0:
            result_text = l(ctx.guild_locale, 'shop.fail')
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
            
        result_text = l(ctx.guild_locale, 'shop.traded', item_name=treasure_loc['name'], amount=amount, price=sell_price)
            
        await user_data.update(
            owned_treasures=owned_treasure,
            wool=user_data.wool + sell_price
        )
        
        await update()
        
    r_treasure_buy = re.compile(r'treasure_buy_(.*)_(.*)_(.*)')
    @component_callback(r_treasure_buy)
    async def buy_treasure_callback(self, ctx: ComponentContext):
        
        await ctx.defer(edit_origin=True)
        
        await self.load_shop(ctx.guild_id)
        
        user_data = await UserData(ctx.author.id).fetch()
        
        match = self.r_treasure_buy.match(ctx.component.custom_id)
        
        if not match:
            return
        
        treasure_id = match.group(1)
        amount_to_buy = match.group(2)
        max_amount = int(match.group(3))
        
        all_treasures = await fetch_treasure()
        
        treasure = DictItem(nid=treasure_id, **all_treasures[treasure_id], type=0)
        
        result_text = ''
        
        treasure_price = treasure.cost * self.daily_shop.stock_price
        
        async def update():
            embed, components = await self.embed_manager(ctx, 'Treasures')
            embed.set_footer(result_text)
            
            await ctx.edit(embed=embed, components=components)
        
        if user_data.wool < treasure_price:
            result_text = l(ctx.guild_id, 'shop.traded_fail')
            return await update()

        current_balance = user_data.wool
        price = 0
        amount = 0
        
        treasure_loc: dict = l(ctx.guild_id, f'items.treasures.{treasure.nid}')
        
        name = treasure_loc['name']
        
        if amount_to_buy == 'max':
            for _ in range(max_amount):
                current_balance -= treasure_price
                
                if current_balance <= 0:
                    break
                
                price += int(treasure_price)
                amount += 1
                
            result_text = l(ctx.guild_locale, 'shop.')
        else:
            price = int(treasure_price)
            amount = 1
        
        result_text = l(ctx.guild_locale, 'shop.traded', item_name=name, amount=amount, price=price)
        
        owned_treasure = user_data.owned_treasures
        
        owned_treasure[treasure_id] = owned_treasure.get(treasure_id, 0) + amount
        
        await user_data.update(
            wool=user_data.wool - price,
            owned_treasures=owned_treasure
        )
        
        return await update()
        
    r_buy_bg = re.compile(r'buy_bg_(.*)_(\d+)')
    @component_callback(r_buy_bg)
    async def buy_bg_callback(self, ctx: ComponentContext):
        
        await ctx.defer(edit_origin=True)
        
        user = await UserData(ctx.author.id).fetch()
        
        match = self.r_buy_bg.match(ctx.component.custom_id)
        
        if not match:
            return
        
        bg_id = match.group(1)
        page = int(match.group(2))
        
        bg_data = await fetch_background()
        bg = DictItem(nid=bg_id, **bg_data)
        
        owned_backgrounds = user.owned_backgrounds
        
        async def update():
            embed, components = await self.embed_manager(ctx, 'Backgrounds', page=page)
            embed.set_footer(result_text)
            
            await ctx.send(embed=embed, components=components, ephemeral=True)
        
        if bg.nid in owned_backgrounds:
            result_text = await loc(ctx.guild_id, 'Shop', 'already_owned')
            return await update()
        
        if user.wool < bg.cost:
            result_text = await loc(ctx.guild_id, 'Shop', 'cannot_buy')
            return await update()
        
        owned_backgrounds.append(bg.nid)
        
        result_text = await loc(ctx.guild_id, 'Shop', 'bought', values={
            'what': await loc(ctx.guild_id, 'Items', 'Backgrounds', bg.nid),
            'cost': fnum(bg.cost)
        })
        
        await user.update(
            owned_backgrounds=owned_backgrounds,
            wool=user.wool - bg.cost
        )
        
        await update()
        
    r_buy_nikogotchi = re.compile(r'nikogotchi_buy_(\d+)')
    @component_callback(r_buy_nikogotchi)
    async def buy_nikogotchi_callback(self, ctx: ComponentContext):
        
        await ctx.defer(edit_origin=True)
        
        user_data = await UserData(ctx.author.id).fetch()
        nikogotchi = await NikogotchiData(ctx.author.id).fetch()
        
        match = self.r_buy_nikogotchi.match(ctx.component.custom_id)
        
        if not match:
            return
        
        capsule_id = int(match.group(1))        
        result_text = ''
        
        capsules = await fetch_item('capsules')
        
        nikogotchi_capsule = Item(**capsules[capsule_id])
        capsule_data = await loc(ctx.guild_id, 'Items', 'capsules', nikogotchi_capsule.id)
        
        async def update():
            embed, components = await self.embed_manager(ctx, 'capsules')
            embed.set_footer(result_text)
            
            await ctx.edit(embed=embed, components=components)
        
        if nikogotchi.data or nikogotchi.nikogotchi_available:
            result_text = await loc(ctx.guild_id, 'Shop', 'already_owned')
            return await update()
        
        if user_data.wool < nikogotchi_capsule.cost:
            result_text = await loc(ctx.guild_id, 'Shop', 'cannot_buy')
            return await update()
        
        await nikogotchi.update(nikogotchi_available=True, rarity=capsule_id)
        await user_data.update(wool=user_data.wool - nikogotchi_capsule.cost)
        
        result_text = await loc(ctx.guild_id, 'Shop', 'bought', values={
            'what': capsule_data['name'],
            'cost': fnum(nikogotchi_capsule.cost)
        })
        
        await update()
        
    r_buy_object = re.compile(r'buy_([^\d]+)_(\d+)')
    @component_callback(r_buy_object)
    async def buy_pancakes_callback(self, ctx: ComponentContext):
        
        await ctx.defer(edit_origin=True)
        
        user_data = await UserData(ctx.author.id).fetch()
        nikogotchi_data = await NikogotchiData(ctx.author.id).fetch()
        
        match = self.r_buy_object.match(ctx.component.custom_id)
        
        if not match:
            return
        
        item_category = match.group(1)
        item_id = int(match.group(2))
        
        result_text = ''
        
        async def update():
            
            embed, components = await self.embed_manager(ctx, item_category, 0)
            
            embed.set_footer(result_text)
            
            return await ctx.edit(embed=embed, components=components)

        item = await fetch_item(item_category, item_id)
        
        item = Item(**item)
            
        if user_data.wool < item.cost:
            result_text = await loc(ctx.guild_id, 'Shop', 'cannot_buy')
            return await update()
        
        result_text = await loc(ctx.guild_id, 'Shop', 'bought', values={
            'what': await loc(ctx.guild_id, 'Items', item_category, item.id, 'name', values={'item': item.id}),
            'cost': fnum(item.cost)
        })
        
        json_data = asdict(nikogotchi_data)
        
        await nikogotchi_data.update(**{item.id: json_data[item.id] + 1})
        
        await user_data.update(wool=user_data.wool - item.cost)
        await update()
        
        
    @component_callback('capsules', 'pancakes', 'Backgrounds', 'Treasures', 'go_back')
    async def main_shop_callbacks(self, ctx: ComponentContext):
        await ctx.defer(edit_origin=True)
        
        await self.load_shop(ctx.guild_id)
        
        embed, components = await self.embed_manager(ctx, ctx.custom_id, {'page': 0})
            
        embed.color = 0x02f2c6
        
        await ctx.edit(embed=embed, components=components)
    
    
    r_page = re.compile(r'page_([^\d]+)_(\d+)')
    @component_callback(r_page)
    async def page_callback(self, ctx: ComponentContext):
        
        await self.load_shop(ctx.guild_id)
        
        await ctx.defer(edit_origin=True)
        
        match = self.r_page.match(ctx.component.custom_id)
        
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
                
        embed, components = await self.embed_manager(ctx, 'Backgrounds', {'page': bg_page})
        
        embed.color = 0x02f2c6
        
        await ctx.edit(embed=embed, components=components)
    
    async def embed_manager(self, ctx: SlashContext, category: str, **kwargs) -> Union[list[BaseComponent], Embed, None]:

        await self.load_shop(ctx.guild_id)
        
        user_data = await UserData(ctx.author.id).fetch()
        
        user_wool: int = user_data.wool
        
        stock: str = await loc(ctx.guild_id, 'Shop', 'stock', values={'stock_price': self.daily_shop.stock_price, 'stock_value': self.daily_shop.stock_value})
        
        key_owned = await loc(ctx.guild_id, 'Shop', 'key_owned')
        key_general = await loc(ctx.guild_id, 'Shop', 'key_general')
        
        wool_counter = await loc(ctx.guild_id, 'Shop', 'user_wool', values={'wool': fnum(user_wool)})
        magpie = EmbedAttachment('https://cdn.discordapp.com/attachments/1025158352549982299/1176956900928131143/Magpie.webp')
        
        go_back = Button(
            style=ButtonStyle.DANGER,
            custom_id='go_back',
            label=await loc(ctx.guild_id, 'Shop', 'go_back')
        )
        
        if category == 'main_shop' or category == 'go_back':
            
            motds = await loc(ctx.guild_id, 'Shop', 'MainShop', 'motds')
            
            motd = motds[self.daily_shop.motd]
                
            title = await loc(ctx.guild_id, 'Shop', 'MainShop', 'title')
            description = await loc(ctx.guild_id, 'Shop', 'MainShop', 'description', values={
                'motd': motd,
                'user_wool': wool_counter
            })
                
            embed = Embed(
                title=title,
                description=description,
                thumbnail=magpie
            )
            
            buttons = [
                    Button(
                        label=await loc(ctx.guild_id, 'Shop', 'MainShop', 'buttons', 'capsules'),
                        emoji=PartialEmoji(id=1147279938660089898),
                        style=ButtonStyle.BLURPLE,
                        custom_id='capsules'
                    ),
                    
                    Button(
                        label=await loc(ctx.guild_id, 'Shop', 'MainShop', 'buttons', 'pancakes'),
                        emoji=PartialEmoji(id=1147281411854839829),
                        style=ButtonStyle.BLURPLE,
                        custom_id='pancakes'
                    ),
                    
                    Button(
                        label=await loc(ctx.guild_id, 'Shop', 'MainShop', 'buttons', 'Backgrounds'),
                        emoji=PartialEmoji(id=1026181558392062032),
                        style=ButtonStyle.BLURPLE,
                        custom_id='Backgrounds'
                    ),
                    
                    Button(
                        label=await loc(ctx.guild_id, 'Shop', 'MainShop', 'buttons', 'Treasures'),
                        emoji=PartialEmoji(id=1026135536190111755),
                        style=ButtonStyle.BLURPLE,
                        custom_id='Treasures'
                    )
                ]
            
            return embed, buttons
        
        elif category == 'capsules':
            
            nikogotchi = await NikogotchiData(ctx.author.id).fetch()
            capsules: dict = await fetch_item()
            
            caspule_text = ''
            buttons = []
            
            for i, capsule in enumerate(capsules):
                
                capsule_data = await loc(ctx.guild_id, 'Items', 'capsules', capsule['id'])
                
                caspule_text += f'<:capsule:{capsule["image"]}>  **{capsule_data["name"]}** - {icon_wool}{fnum(capsule["cost"])}\n*{capsule_data["description"]}*\n\n'
                
                button = Button(
                    label=await loc(ctx.guild_id, 'Shop', 'buy'),
                    emoji=PartialEmoji(id=capsule["image"]),
                    style=ButtonStyle.BLURPLE,
                    custom_id=f'nikogotchi_buy_{i}'
                )
                
                if nikogotchi.nikogotchi_available or nikogotchi.data:
                    button.disabled = True
                    button.style = ButtonStyle.RED
                
                if user_wool < capsule['cost']:
                    button.disabled = True
                    button.style = ButtonStyle.GRAY
                    
                buttons.append(button)
                
            buttons.append(go_back)
                
            title = await loc(ctx.guild_id, 'Shop', 'Capsules', 'title')
            description = await loc(ctx.guild_id, 'Shop', 'Capsules', 'description', values={'capsules': caspule_text, 'user_wool': wool_counter, 'key': key_owned})
            
            embed = Embed(
                title=title,
                description=description,
                thumbnail=magpie
            )
            
            return embed, buttons
        elif category == 'pancakes':
        
            pancake_data = await fetch_item('pancakes')
            
            nikogotchi_data = await NikogotchiData(ctx.author.id).fetch()
            json_data = asdict(nikogotchi_data)
            
            pancake_text = ''
            buttons: list[Button] = []
            for id_, pancake in enumerate(pancake_data):
                
                pancake = Item(**pancake)
                
                owned = json_data[pancake.id]
                
                amount_owned = await loc(ctx.guild_id, 'Shop', 'currently_owned', values={'amount': owned})
                pancake_loc = await loc(ctx.guild_id, 'Items', 'pancakes', pancake.id)
                
                pancake_text += f'''
                <:pancake:{pancake.image}>  **{pancake_loc['name']}** - {icon_wool}{fnum(pancake.cost)}
                *{pancake_loc['description']}*
                {amount_owned}\n'''
                
                button = Button(
                    label=await loc(ctx.guild_id, 'Shop', 'buy'),
                    emoji=PartialEmoji(id=pancake.image),
                    style=ButtonStyle.BLURPLE,
                    custom_id=f'buy_pancakes_{id_}'
                )
                
                if user_wool < pancake.cost:
                    button.disabled = True
                    button.style = ButtonStyle.GRAY
                
                buttons.append(button)
                
            buttons.append(go_back)
                
            title = await loc(ctx.guild_id, 'Shop', 'Pancakes', 'title')
            description = await loc(ctx.guild_id, 'Shop', 'Pancakes', 'description', values={'key': key_general, 'pancakes': pancake_text, 'user_wool': wool_counter})
                
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
            
            background_name = await loc(ctx.guild_id, 'Items', 'Backgrounds', background.nid)
            background_description = await loc(ctx.guild_id, 'Shop', 'Backgrounds', 'description', values={
                'cost': fnum(background.cost),
                'key': key_owned,
                'name': background_name,
                'user_wool': wool_counter
            })
            
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
                    label=await loc(ctx.guild_id, 'Shop', 'buy'),
                    style=ButtonStyle.GREEN,
                    custom_id=f'buy_bg_{background.nid}_{bg_page}'
                ),
                Button(
                    label=await loc(ctx.guild_id, 'Shop', 'go_back'),
                    style=ButtonStyle.DANGER,
                    custom_id='go_back'
                ),
                Button(
                    label='>',
                    style=ButtonStyle.BLURPLE,
                    custom_id=f'page_next_{bg_page}'
                )
            ]
            
            buy_button = buttons[1]
            
            if user_wool < background.cost:
                buy_button.disabled = True
                buy_button.style = ButtonStyle.GRAY
            
            if background.nid in user_backgrounds:
                buy_button.disabled = True
                buy_button.style = ButtonStyle.RED
                
            buttons[1] = buy_button
            
            return embed, buttons
            
        elif category == 'Treasures':
            
            treasure_stock = self.daily_shop.treasure_stock
            
            treasure_text = ''
            buttons: list[Button] = []
            bottom_buttons: list[Button] = []
            
            user_data = await UserData(ctx.author.id).fetch()
            
            owned = user_data.owned_treasures
            
            for treasure in treasure_stock:
                
                price = int(treasure.cost * self.daily_shop.stock_price)
                
                amount_owned = await loc(ctx.guild_id, 'Shop', 'currently_owned', values={'amount': owned.get(treasure.nid, 0)})
                treasure_loc = await loc(ctx.guild_id, 'Items', 'Treasures', treasure.nid)
                
                treasure_text += f'''
                <:treasure:{treasure.image}>  **{treasure_loc['name']}** - ~~{icon_wool}{fnum(treasure.cost)}~~ - {icon_wool}{fnum(price)}
                *{treasure_loc['description']}*
                {amount_owned}\n'''
                
                button = Button(
                    label=await loc(ctx.guild_id, 'Shop', 'buy'),
                    emoji=PartialEmoji(id=treasure.image),
                    style=ButtonStyle.BLURPLE,
                    custom_id=f'treasure_buy_{treasure.nid}_One'
                )
                
                if user_wool < price:
                    button.disabled = True
                    
                buttons.append(button)
                
                bottom_button = Button(
                    label=await loc(ctx.guild_id, 'Shop', 'buy_all'),
                    emoji=PartialEmoji(id=treasure.image),
                    style=ButtonStyle.BLURPLE,
                    custom_id=f'treasure_buy_{treasure.nid}_All'
                )
                
                if user_wool < price:
                    bottom_button.disabled = True
                    
                bottom_buttons.append(bottom_button)
                
            buttons.append(go_back)
            bottom_buttons.append(Button(
                label=await loc(ctx.guild_id, 'Shop', 'sell_button'),
                style=ButtonStyle.GREEN,
                custom_id='sell_treasure_menu'
            ))
            
            title = await loc(ctx.guild_id, 'Shop', 'Treasures', 'title')
            
            description = await loc(ctx.guild_id, 'Shop', 'Treasures', 'description', values={'key': key_general, 'treasures': treasure_text, 'user_wool': wool_counter, 'wool_market': stock})
            
            embed = Embed(
                title=title,
                description=description,
                thumbnail=magpie
            )
            
            return embed, [ActionRow(*buttons), ActionRow(*bottom_buttons)]
        
        elif category == 'Sell_Treasures':
            
            selected_treasure = kwargs['selected_treasure']
            selected_treasure_data = None
            sell_price_one = 0
            sell_price_all = 0
            
            user_data = await UserData(ctx.author.id).fetch()
            
            owned = user_data.owned_treasures
            all_treasures = await fetch_treasure('all')
            
            if selected_treasure is not None:
                selected_treasure = DictItem(nid=selected_treasure, **all_treasures[selected_treasure], type=0)
                selected_treasure_data = await loc(ctx.guild_id, 'Items', 'Treasures', selected_treasure.nid)
                
                sell_price_one = int(selected_treasure.cost * self.daily_shop.stock_price)
                sell_price_all = int(selected_treasure.cost * self.daily_shop.stock_price * owned[selected_treasure.nid])
            
            treasure_selection = []
            
            for treasure_nid, amount in owned.items():
                
                if amount <= 0:
                    continue
                
                treasure = DictItem(nid=treasure_nid, **all_treasures[treasure_nid], type=0)
                
                treasure_data = await loc(ctx.guild_id, 'Items', 'Treasures', treasure_nid)
                
                emoji=PartialEmoji(id=int(treasure.image))
                
                treasure_selection.append(
                    
                    StringSelectOption(
                        label=f'{treasure_data["name"]} (x{amount})',
                        value=treasure_nid,
                        description=treasure_data['description'],
                        emoji=emoji,
                    )
                )
                
            selection_description = ''
            
            if selected_treasure is not None:
                treasure_id = selected_treasure.nid
            else:
                treasure_id = 0
            
            buttons = [
                Button(
                    label=await loc(ctx.guild_id, 'Shop', 'sell'),
                    custom_id=f'treasure_sell_{treasure_id}_one',
                    style=ButtonStyle.GREEN
                ),
                Button(
                    label=await loc(ctx.guild_id, 'Shop', 'sell_all', values={'amount': 0}),
                    custom_id=f'treasure_sell_{treasure_id}_all',
                    style=ButtonStyle.GREEN
                ),
                go_back
            ]
            
            if selected_treasure is not None:
                selection_description = await loc(ctx.guild_id, 'Shop', 'Treasure_Sell', 'treasure_selected', values={
                    'selected_treasure': f"<:treasure:{selected_treasure.image}> {selected_treasure_data['name']}",
                    'sell_one': fnum(sell_price_one),
                    'sell_all': fnum(sell_price_all)
                })
                
                buttons[1].label = await loc(ctx.guild_id, 'Shop', 'sell_all', values={'amount': owned[selected_treasure.nid]})       
            else:
                selection_description = await loc(ctx.guild_id, 'Shop', 'Treasure_Sell', 'treasure_not_selected')
                
            embed = Embed(
                title=await loc(ctx.guild_id, 'Shop', 'Treasure_Sell', 'title'),
                description=await loc(ctx.guild_id, 'Shop', 'Treasure_Sell', 'description', values={
                    'wool_market': stock,
                    'user_wool': wool_counter,
                    'selected_treasure': selection_description
                }),
                thumbnail=magpie
            )
            
            select_menu = None
            
            if len(treasure_selection) > 0:
                select_menu = StringSelectMenu(
                    *treasure_selection,
                    placeholder=await loc(ctx.guild_id, 'Shop', 'Treasure_Sell', 'select_treasure_placeholder'),
                    custom_id=f'select_treasure',
                )
            else:
                select_menu = StringSelectMenu(
                    '💥💥💥💥💥💥💥💥💥💥💥💥',
                    placeholder=await loc(ctx.guild_id, 'Shop', 'Treasure_Sell', 'select_no_treasures :('),
                    custom_id=f'select_treasure',
                    disabled=True
                )
            
            if selected_treasure is None:
                buttons[0].disabled = True
                buttons[0].style = ButtonStyle.GREY
                buttons[1].disabled = True
                buttons[1].style = ButtonStyle.GREY
                
            components = [ActionRow(select_menu), ActionRow(*buttons)]
                
            return embed, components
        
    @slash_command(description="Open the Shop!")
    async def shop(self, ctx: SlashContext):
        
        await ctx.defer(ephemeral=True)
        
        await self.load_shop(ctx.guild_id)
        
        embed, button = await self.embed_manager(ctx, 'main_shop')
        embed.color = 0x02f2c6
        
        await ctx.send(embed=embed, components=button)