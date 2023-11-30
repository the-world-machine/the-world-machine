from typing import Union
from interactions import *
from interactions.api.events import Component
from Utilities.fancysend import *
from Utilities.bot_icons import *
from Utilities.ShopData import Item, ShopData, fetch_shop_data, reset_shop_data
from Utilities.CommandHandler import twm_cmd, twm_subcmd
from datetime import datetime, timedelta
from database import Database
from Localization.Localization import loc, l_num
import re


class Shop(Extension):
    
    daily_shop: ShopData = None
    
    async def load_shop(self, guild_id: int):
        data = await fetch_shop_data()
        
        old_time = data.last_reset_date
        now = datetime.now()
        
        should_reset = now > old_time + timedelta(days=1)
        
        if should_reset:
            data = await reset_shop_data(guild_id)
        
        self.daily_shop = data
        
    r_buy_object = re.compile(r'buy_([^\d]+)_(\d+)')
    @component_callback(r_buy_object)
    async def buy_callback(self, ctx: ComponentContext):
        
        await ctx.defer(edit_origin=True)
        
        match = self.r_buy_object.match(ctx.component.custom_id)
        
        if not match:
            return
        
        item_category = match.group(1)
        item_id = int(match.group(2))
        
        footer_text = ''
        
        async def update():
            embed, components = await self.embed_manager(ctx, item_category)
            
            embed.set_footer(footer_text)
            
            return await ctx.edit(embed=embed, components=components)
        
        user_wool = await Database.fetch('user_data', 'wool', ctx.author.id)
        items = await Database.get_items(item_category)
        item = Item(items[item_id])
        
        if item.type == 'treasure':
            item.cost = item.cost * self.daily_shop.stock_price
            
        if item.type == 'capsule':
            
            nikogotchi = await Database.fetch('nikogotchi_data', 'nikogotchi_available', ctx.author.id)

            if nikogotchi > 0:
                footer_text = await loc(ctx.guild_id, 'Shop', 'already_owned')
                return await update()
            
        if user_wool < item.cost:
            footer_text = await loc(ctx.guild_id, 'Shop', 'cannot_buy')
            return await update()
        
        footer_text = await loc(ctx.guild_id, 'Shop', 'bought', values={
            'what': await loc(ctx.guild_id, 'Items', item_category, item.nid, 'name', values={'item': item.nid}),
            'cost': l_num(item.cost)
        })
        
        if item.type == 'treasure':
            treasure = await Database.fetch('nikogotchi_data', 'treasure', ctx.author.id)
            treasure[item_id] += 1
            
            await Database.update('nikogotchi_data', 'treasure', ctx.author.id, treasure)
            
        if item.type == 'capsule':
            nikogotchi_available = await Database.fetch('nikogotchi_data', 'nikogotchi_available', ctx.author.id)
            nikogotchi_available += 1
            
            await Database.update('nikogotchi_data', 'nikogotchi_available', ctx.author.id, nikogotchi_available)
            
        if item.type == 'pancakes':
            pancake = await Database.fetch('nikogotchi_data', item.nid, ctx.author.id)
            pancake += 1
            
            await Database.update('nikogotchi_data', item.nid, ctx.author.id, pancake)
      
        await Database.update('user_data', 'wool', ctx.author.id, user_wool - item.cost)
        
        await update()
        
        
    @component_callback('capsules', 'pancakes', 'backgrounds', 'treasures', 'go_back')
    async def main_shop_callbacks(self, ctx: ComponentContext):
        await ctx.defer(edit_origin=True)
        
        await self.load_shop(ctx.guild_id)
        
        embed, components = await self.embed_manager(ctx, ctx.custom_id)
            
        embed.color = 0x02f2c6
        
        await ctx.edit(embed=embed, components=components)
    
    async def embed_manager(self, ctx: SlashContext, category: str, shop_args: dict = {}) -> Union[list[BaseComponent], Embed, None]:

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
            
            t_stock = ''
            
            for item in self.daily_shop.treasure_stock:
                
                item_data = await loc(ctx.guild_id, 'Items', 'Treasures', item.nid)
                
                t_stock += f'- <:any:{item.image}> **{item_data["name"]}** - *{item_data["description"]}*\n'
                
            bg_stock = ''
            
            for bg in self.daily_shop.background_stock:
                
                bg_data = await loc(ctx.guild_id, 'Items', 'backgrounds', bg.nid)
                
                bg_stock += f'- {bg_data}\n'
                
            title = await loc(ctx.guild_id, 'Shop', 'MainShop', 'title')
            description = await loc(ctx.guild_id, 'Shop', 'MainShop', 'description', values={
                'motd': motd,
                'treasure_stock': t_stock,
                'background_stock': bg_stock,
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
                        label=await loc(ctx.guild_id, 'Shop', 'MainShop', 'buttons', 'backgrounds'),
                        emoji=PartialEmoji(id=1026181558392062032),
                        style=ButtonStyle.BLURPLE,
                        custom_id='backgrounds'
                    ),
                    
                    Button(
                        label=await loc(ctx.guild_id, 'Shop', 'MainShop', 'buttons', 'treasures'),
                        emoji=PartialEmoji(id=1026135536190111755),
                        style=ButtonStyle.BLURPLE,
                        custom_id='treasures'
                    )
                ]
            
            return embed, buttons
        
        elif category == 'capsules':
            
            nikogotchi: int = await Database.fetch('nikogotchi_data', 'nikogotchi_available', ctx.author.id)
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
                    custom_id=f'buy_capsule_{i}'
                )
                
                if user_wool < capsule['price']:
                    button.disabled = True
                    button.style = ButtonStyle.GRAY
                    
                if nikogotchi > 0:
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
                {amount_owned}\n\n'''
                
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
            

    @twm_cmd(description="Open the Shop!", ephemeral=True)
    async def shop(self, ctx: SlashContext):
        
        await self.load_shop(ctx.guild_id)
        
        embed, button = await self.embed_manager(ctx, 'main_shop')
        embed.color = 0x02f2c6
        
        await ctx.send(embed=embed, components=button)