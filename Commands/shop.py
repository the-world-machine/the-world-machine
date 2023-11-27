from typing import Union
from interactions import *
from Utilities.fancysend import *
from Utilities.bot_icons import *
from Utilities.ShopData import Shop_, fetch_shop_data
from Utilities.CommandHandler import twm_cmd, twm_subcmd
from datetime import datetime
from database import Database
from Localization.Localization import loc, loc_item, loc_bg


class Command(Extension):
    
    daily_shop: Shop_ = None
    
    async def load_shop(self):
        data = await fetch_shop_data()
        
        old_time = data.last_reset_date
        now = datetime.now().timestamp()
        
        should_reset = now > old_time + 86400
        
        if should_reset:
            pass
        
        self.daily_shop = data
    
    async def embed_manager(self, ctx: SlashContext, embed: str, shop_args: dict = {}) -> Union[list[BaseComponent], Embed, None]:

        user_wool = await Database.fetch('user_data', 'wool', ctx.author.id)
        
        wool_counter = await loc(ctx.guild_id, 'Shop', 'user_wool', values={'wool': user_wool})
        magpie = EmbedAttachment('https://cdn.discordapp.com/attachments/1025158352549982299/1176956900928131143/Magpie.webp')
        
        if embed == 'main_shop':
            
            motds = await loc(ctx.guild_id, 'Shop', 'MainShop', 'motds')
            
            motd = motds[self.daily_shop.motd]
            
            t_stock = ''
            
            for item in self.daily_shop.treasure_stock:
                
                item_data = await loc(ctx.guild_id, 'Items', 'Treasures', item.nid)
                
                t_stock += f'<:any:{item.image}> **{item_data["name"]}** - *{item_data["description"]}*\n'
                
            bg_stock = ''
            
            for bg in self.daily_shop.background_stock:
                
                bg_data = await loc_bg(ctx.guild_id, bg.nid)
                
                bg_stock += f'**{bg_data}**\n'
            
            return(
                
                Embed(
                    title=await loc(ctx.guild_id, 'Shop', 'MainShop', 'title'),
                    description=await loc(ctx.guild_id, 'Shop', 'MainShop', 'description', values={
                        'motd': motd,
                        'treasure_stock': t_stock,
                        'background_stock': bg_stock,
                        'user_wool': wool_counter
                    }),
                    thumbnail=magpie
                ),
            
                [
                    Button(
                        label=await loc(ctx.guild_id, 'Shop', 'MainShop', 'buttons', 'capsules'),
                        emoji=
                    )
                ]
            ),
            

    @twm_cmd(description="Open the Shop!", ephemeral=True)
    async def shop(self, ctx: SlashContext):
        
        await self.load_shop()
        
        embed, button = self.embed_manager(ctx, 'main_shop')
        
        await ctx.send(embed=await )