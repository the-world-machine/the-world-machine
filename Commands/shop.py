from typing import Union
from interactions import *
from interactions.api.events import Component
from Utilities.fancysend import *
from Utilities.bot_icons import *
from Utilities.ShopData import Background, Item, ShopData, fetch_shop_data, reset_shop_data
from Utilities.CommandHandler import twm_cmd, twm_subcmd
from datetime import datetime, timedelta
from database import Database
from Localization.Localization import loc, l_num
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
        
        treasure = int(ctx.values[0])
        
        embed, components = await self.embed_manager(ctx, 'Sell_Treasures', {'selected_treasure': treasure})
        
        await ctx.edit(embed=embed, components=components)

    @component_callback('sell_treasure_menu')
    async def sell_treasure_callback(self, ctx: ComponentContext):
        
        await ctx.defer(edit_origin=True)
        
        await self.load_shop(ctx.guild_id)
        
        embed, components = await self.embed_manager(ctx, 'Sell_Treasures', {'selected_treasure': None})
        
        await ctx.edit(embed=embed, components=components)
        
    r_treasure_sell = re.compile(r'treasure_sell_(.*)_(.*)')
    @component_callback(r_treasure_sell)
    async def treasure_sell_action_callback(self, ctx: ComponentContext):
        
        await ctx.defer(edit_origin=True)
        
        await self.load_shop(ctx.guild_id)
        
        match = self.r_treasure_sell.search(ctx.component.custom_id)
        
        if not match:
            return
        
        treasure_id = int(match.group(1))
        amount_to_sell = match.group(2)
        
        stock_price = self.daily_shop.stock_price
        
        all_treasures = await Database.get_items('Treasures')
        owned_treasure = await Database.fetch('nikogotchi_data', 'treasure', ctx.author.id)
        
        amount_of_treasure = owned_treasure[treasure_id]
        
        treasure = Item(all_treasures[treasure_id])
        
        footer_text = ''
        
        treasure_data = await loc(ctx.guild_id, 'Items', 'Treasures', treasure.nid)
        
        async def update():
            
            if amount_to_sell == 'all':
                embed, components = await self.embed_manager(ctx, 'Sell_Treasures', {'selected_treasure': None})
            else:
                embed, components = await self.embed_manager(ctx, 'Sell_Treasures', {'selected_treasure': treasure_id})
            
            embed.set_footer(footer_text)
            
            await ctx.edit(embed=embed, components=components)
            
        if amount_of_treasure <= 0:
            footer_text = f"You don't have any {treasure_data['name']} to sell!"
            await update()
            return
            
        sell_price = 0
            
        if amount_to_sell == 'all':
            sell_price = int(amount_of_treasure * treasure.cost * stock_price)
            owned_treasure[treasure_id] = 0
            
            footer_text = await loc(ctx.guild_id, 'Shop', 'sold_all', values={'what': treasure_data['name'], 'amount': l_num(amount_of_treasure), 'cost': l_num(sell_price)})
        else:
            sell_price = int(treasure.cost * stock_price)
            owned_treasure[treasure_id] -= 1
            
            footer_text = await loc(ctx.guild_id, 'Shop', 'sold', values={'what': treasure_data['name'], 'cost': l_num(sell_price)})
            
        await Database.update('nikogotchi_data', 'treasure', ctx.author.id, owned_treasure)
        
        user_wool = await Database.fetch('user_data', 'wool', ctx.author.id)
        
        await Database.update('user_data', 'wool', ctx.author.id, user_wool + sell_price)
        
        await update()
        
    r_treasure_buy = re.compile(r'treasure_buy_(\d+)_([^\d]+)')
    @component_callback(r_treasure_buy)
    async def buy_treasure_callback(self, ctx: ComponentContext):
        
        await ctx.defer(edit_origin=True)
        
        await self.load_shop(ctx.guild_id)
        
        user_wool = await Database.fetch('user_data', 'wool', ctx.author.id)
        
        match = self.r_treasure_buy.match(ctx.component.custom_id)
        
        if not match:
            return
        
        treasure_id = int(match.group(1))
        amount_to_buy = match.group(2)
        
        all_treasures = await Database.get_items('Treasures')
        
        treasure = Item(all_treasures[treasure_id])
        
        footer_text = ''
        
        treasure_price = treasure.cost * self.daily_shop.stock_price
        
        async def update():
            embed, components = await self.embed_manager(ctx, 'Treasures')
            embed.set_footer(footer_text)
            
            await ctx.edit(embed=embed, components=components)
        
        if user_wool < treasure_price:
            footer_text = 'You cannot afford this item.'
            return await update()

        current_cost = user_wool
        price = 0
        amount = 0
        
        t_data = await loc(ctx.guild_id, 'Items', 'Treasures', treasure.nid)
        
        name = t_data['name']
        
        if amount_to_buy == 'All':
            while True:
                current_cost -= treasure_price
                
                if current_cost <= 0:
                    break
                
                price += int(treasure_price)
                amount += 1
                
            footer_text = await loc(ctx.guild_id, 'Shop', 'bought_all', values={'what': name, 'cost': l_num(price), 'amount': l_num(amount)})
        else:
            current_cost -= treasure_price
            price = int(treasure_price)
            amount = 1
            footer_text = await loc(ctx.guild_id, 'Shop', 'bought', values={'what': name, 'cost': l_num(price)})
        
        owned_treasure = await Database.fetch('nikogotchi_data', 'treasure', ctx.author.id)
        
        owned_treasure[treasure_id] += amount
        
        await Database.update('nikogotchi_data', 'treasure', ctx.author.id, owned_treasure)
        
        await Database.update('user_data', 'wool', ctx.author.id, user_wool - price)
        
        
        return await update()
        
    r_buy_bg = re.compile(r'buy_bg_(\d+)_(\d+)')
    @component_callback(r_buy_bg)
    async def buy_bg_callback(self, ctx: ComponentContext):
        
        await ctx.defer(edit_origin=True)
        
        user_wool = await Database.fetch('user_data', 'wool', ctx.author.id)
        
        match = self.r_buy_bg.match(ctx.component.custom_id)
        
        all_bgs = await Database.get_items('Backgrounds')
        
        if not match:
            return
        
        bg_id = int(match.group(1))
        page = int(match.group(2))
        
        bg = Background(all_bgs[bg_id])
        
        owned_backgrounds = await Database.fetch('user_data', 'unlocked_backgrounds', ctx.author.id)
        
        async def update():
            embed, components = await self.embed_manager(ctx, 'Backgrounds', {'page': page})
            embed.set_footer(footer_text)
            
            await ctx.send(embed=embed, components=components, ephemeral=True)
        
        if bg.id_ in owned_backgrounds:
            footer_text = await loc(ctx.guild_id, 'Shop', 'already_owned')
            return await update()
        
        if user_wool < bg.cost:
            footer_text = await loc(ctx.guild_id, 'Shop', 'cannot_buy')
            return await update()
        
        owned_backgrounds.append(bg.id_)
        
        await Database.update('user_data', 'unlocked_backgrounds', ctx.author.id, owned_backgrounds)
        
        footer_text = await loc(ctx.guild_id, 'Shop', 'bought', values={
            'what': await loc(ctx.guild_id, 'Items', 'Backgrounds', bg.nid),
            'cost': l_num(bg.cost)
        })
            
        await Database.update('user_data', 'wool', ctx.author.id, user_wool - bg.cost)
        
        await update()
        
    r_buy_nikogotchi = re.compile(r'nikogotchi_buy_(\d+)')
    @component_callback(r_buy_nikogotchi)
    async def buy_nikogotchi_callback(self, ctx: ComponentContext):
        
        await ctx.defer(edit_origin=True)
        
        match = self.r_buy_nikogotchi.match(ctx.component.custom_id)
        
        if not match:
            return
        
        capsule_id = int(match.group(1))        
        footer_text = ''
        
        capsules = await Database.get_items('capsules')
        
        nikogotchi_capsule = Item(capsules[capsule_id])
        capsule_data = await loc(ctx.guild_id, 'Items', 'capsules', nikogotchi_capsule.nid)
        
        async def update():
            embed, components = await self.embed_manager(ctx, 'capsules')
            embed.set_footer(footer_text)
            
            await ctx.edit(embed=embed, components=components)
            
        user_wool = await Database.fetch('user_data', 'wool', ctx.author.id)
        nikogotchi = await Database.fetch('nikogotchi_data', 'data', ctx.author.id)
        rarity = await Database.fetch('nikogotchi_data', 'rarity', ctx.author.id)
        
        if nikogotchi or rarity > -1:
            footer_text = await loc(ctx.guild_id, 'Shop', 'already_owned')
            return await update()
        
        if user_wool < nikogotchi_capsule.cost:
            footer_text = await loc(ctx.guild_id, 'Shop', 'cannot_buy')
            return await update()
        
        await Database.update('nikogotchi_data', 'rarity', ctx.author.id, capsule_id)
        await Database.update('user_data', 'wool', ctx.author.id, user_wool - nikogotchi_capsule.cost)
        
        footer_text = await loc(ctx.guild_id, 'Shop', 'bought', values={
            'what': capsule_data['name'],
            'cost': l_num(nikogotchi_capsule.cost)
        })
        
        await update()
        
    r_buy_object = re.compile(r'buy_([^\d]+)_(\d+)')
    @component_callback(r_buy_object)
    async def buy_callback(self, ctx: ComponentContext):
        
        await ctx.defer(edit_origin=True)
        
        match = self.r_buy_object.match(ctx.component.custom_id)
        
        if not match:
            return
        
        item_category = match.group(1)
        item_id = int(match.group(2))
    
        try:
            bg_page = int(match.group(3))
        except:
            bg_page = 0
        
        footer_text = ''
        
        async def update():
            
            embed, components = await self.embed_manager(ctx, item_category, bg_page)
            
            embed.set_footer(footer_text)
            
            return await ctx.edit(embed=embed, components=components)
        
        user_wool = await Database.fetch('user_data', 'wool', ctx.author.id)
        items = await Database.get_items(item_category)
        
        item = Item(items[item_id])
        
        if item.type == 'Treasures':
            item.cost = item.cost * self.daily_shop.stock_price
            
        if user_wool < item.cost:
            footer_text = await loc(ctx.guild_id, 'Shop', 'cannot_buy')
            return await update()
        
        footer_text = await loc(ctx.guild_id, 'Shop', 'bought', values={
            'what': await loc(ctx.guild_id, 'Items', item_category, item.nid, 'name', values={'item': item.nid}),
            'cost': l_num(item.cost)
        })
        
        if item.type == 'Treasures':
            treasure = await Database.fetch('nikogotchi_data', 'treasure', ctx.author.id)
            treasure[item_id] += 1
            
            await Database.update('nikogotchi_data', 'treasure', ctx.author.id, treasure)
            
        if item.type == 'pancakes':
            pancake = await Database.fetch('nikogotchi_data', item.nid, ctx.author.id)
            pancake += 1
            
            await Database.update('nikogotchi_data', item.nid, ctx.author.id, pancake)
        
        await Database.update('user_data', 'wool', ctx.author.id, user_wool - item.cost)
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
    
    async def embed_manager(self, ctx: SlashContext, category: str, args: dict = None) -> Union[list[BaseComponent], Embed, None]:

        await self.load_shop(ctx.guild_id)
        
        user_wool: int = await Database.fetch('user_data', 'wool', ctx.author.id)
        
        stock: str = await loc(ctx.guild_id, 'Shop', 'stock', values={'stock_price': self.daily_shop.stock_price, 'stock_value': self.daily_shop.stock_value})
        
        key_owned = await loc(ctx.guild_id, 'Shop', 'key_owned')
        key_general = await loc(ctx.guild_id, 'Shop', 'key_general')
        
        wool_counter = await loc(ctx.guild_id, 'Shop', 'user_wool', values={'wool': l_num(user_wool)})
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
            
            nikogotchi = await Database.fetch('nikogotchi_data', 'data', ctx.author.id)
            rarity = await Database.fetch('nikogotchi_data', 'rarity', ctx.author.id)
            capsules: dict = await Database.get_items('capsules')
            
            caspule_text = ''
            buttons = []
            
            for i, capsule in enumerate(capsules):
                
                capsule_data = await loc(ctx.guild_id, 'Items', 'capsules', capsule['nid'])
                
                caspule_text += f'<:capsule:{capsule["image"]}>  **{capsule_data["name"]}** - {wool()}{l_num(capsule["price"])}\n*{capsule_data["description"]}*\n\n'
                
                button = Button(
                    label=await loc(ctx.guild_id, 'Shop', 'buy'),
                    emoji=PartialEmoji(id=capsule["image"]),
                    style=ButtonStyle.BLURPLE,
                    custom_id=f'nikogotchi_buy_{i}'
                )
                
                if user_wool < capsule['price']:
                    button.disabled = True
                    button.style = ButtonStyle.GRAY
                    
                if rarity > -1 or nikogotchi:
                    button.disabled = True
                    button.style = ButtonStyle.RED
                    
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
        
            pancake_data = await Database.get_items('pancakes')
            
            pancakes: list[Item] = []
            for pancake in pancake_data:
                pancakes.append(Item(pancake))
            
            pancake_text = ''
            buttons: list[Button] = []
            for id_, pancake in enumerate(pancakes):
                
                owned = await Database.fetch('nikogotchi_data', pancake.nid, ctx.author.id)
                
                amount_owned = await loc(ctx.guild_id, 'Shop', 'currently_owned', values={'amount': owned})
                pancake_loc = await loc(ctx.guild_id, 'Items', 'pancakes', pancake.nid)
                
                pancake_text += f'''
                <:pancake:{pancake.image}>  **{pancake_loc['name']}** - {wool()}{l_num(pancake.cost)}
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
            
            bg_page = args['page']
            
            background = self.daily_shop.background_stock[bg_page]
            user_backgrounds = await Database.fetch('user_data', 'unlocked_backgrounds', ctx.author.id)
            
            background_name = await loc(ctx.guild_id, 'Items', 'Backgrounds', background.nid)
            background_description = await loc(ctx.guild_id, 'Shop', 'Backgrounds', 'description', values={
                'cost': l_num(background.cost),
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
                    custom_id=f'buy_bg_{background.id_}_{bg_page}'
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
            
            if background.id_ in user_backgrounds:
                buy_button.disabled = True
                buy_button.style = ButtonStyle.RED
                
            buttons[1] = buy_button
            
            return embed, buttons
            
        elif category == 'Treasures':
            
            treasure_stock = self.daily_shop.treasure_stock
            
            treasure_text = ''
            buttons: list[Button] = []
            bottom_buttons: list[Button] = []
            
            for id_, treasure in enumerate(treasure_stock):
                
                price = int(treasure.cost * self.daily_shop.stock_price)
                
                owned = await Database.fetch('nikogotchi_data', 'treasure', ctx.author.id)
                
                amount_owned = await loc(ctx.guild_id, 'Shop', 'currently_owned', values={'amount': owned[treasure.id_]})
                treasure_loc = await loc(ctx.guild_id, 'Items', 'Treasures', treasure.nid)
                
                treasure_text += f'''
                <:treasure:{treasure.image}>  **{treasure_loc['name']}** - ~~{wool()}{l_num(treasure.cost)}~~ - {wool()}{l_num(price)}
                *{treasure_loc['description']}*
                {amount_owned}\n'''
                
                button = Button(
                    label=await loc(ctx.guild_id, 'Shop', 'buy'),
                    emoji=PartialEmoji(id=treasure.image),
                    style=ButtonStyle.BLURPLE,
                    custom_id=f'treasure_buy_{treasure.id_}_One'
                )
                
                if user_wool < price:
                    button.disabled = True
                    
                buttons.append(button)
                
                bottom_button = Button(
                    label=await loc(ctx.guild_id, 'Shop', 'buy_all'),
                    emoji=PartialEmoji(id=treasure.image),
                    style=ButtonStyle.BLURPLE,
                    custom_id=f'treasure_buy_{treasure.id_}_All'
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
            
            selected_treasure = args['selected_treasure']
            selected_treasure_data = None
            sell_price_one = 0
            sell_price_all = 0
            
            owned_treasures = await Database.fetch('nikogotchi_data', 'treasure', ctx.author.id)
            all_treasures = await Database.get_items('Treasures')
            
            if selected_treasure is not None:
                selected_treasure = Item(all_treasures[selected_treasure])
                selected_treasure_data = await loc(ctx.guild_id, 'Items', 'Treasures', selected_treasure.nid)
                
                sell_price_one = int(selected_treasure.cost * self.daily_shop.stock_price)
                sell_price_all = int(selected_treasure.cost * self.daily_shop.stock_price * owned_treasures[selected_treasure.id_])
            
            treasure_selection = []
            
            for i, amount in enumerate(owned_treasures):
                
                if owned_treasures[i] <= 0:
                    continue
                
                treasure = Item(all_treasures[i])
                
                treasure_data = await loc(ctx.guild_id, 'Items', 'Treasures', treasure.nid)
                
                treasure_selection.append(
                    StringSelectOption(
                        label=f'{treasure_data["name"]} (x{amount})',
                        value=str(i),
                        description=treasure_data['description'],
                        emoji=PartialEmoji(id=treasure.image),
                    )
                )
                
            selection_description = ''
            
            if selected_treasure is not None:
                selection_description = await loc(ctx.guild_id, 'Shop', 'Treasure_Sell', 'treasure_selected', values={
                    'selected_treasure': f"<:treasure:{selected_treasure.image}> {selected_treasure_data['name']}",
                    'sell_one': l_num(sell_price_one),
                    'sell_all': l_num(sell_price_all),
                })             
            else:
                selection_description = await loc(ctx.guild_id, 'Shop', 'Treasure_Sell', 'treasure_not_selected')
                
            embed = Embed(
                title=await loc(ctx.guild_id, 'Shop', 'Treasure_Sell', 'title'),
                description=await loc(ctx.guild_id, 'Shop', 'Treasure_Sell', 'description', values={
                    'wool_market': stock,
                    'user_wool': wool_counter,
                    'selected_treasure': selection_description,
                    'currently_owned': await loc(ctx.guild_id, 'Shop', 'currently_owned', values={'amount': amount}),
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
                
            if selected_treasure is not None:
                treasure_id = selected_treasure.id_
            else:
                treasure_id = 0
            
            buttons = [
                Button(
                    label=await loc(ctx.guild_id, 'Shop', 'sell'),
                    custom_id=f'treasure_sell_{treasure_id}_one',
                    style=ButtonStyle.GREEN
                ),
                Button(
                    label=await loc(ctx.guild_id, 'Shop', 'sell_all'),
                    custom_id=f'treasure_sell_{treasure_id}_all',
                    style=ButtonStyle.GREEN
                ),
                go_back
            ]
            
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