from datetime import datetime
import random
from typing import Union
import aiofiles
import json

from interactions import SlashContext
from utilities.shop.fetch_items import fetch_background, fetch_item, fetch_treasure
import database
from localization.loc import l
from dataclasses import dataclass
import json

@dataclass
class DictItem:
    nid: str
    cost: int
    image: Union[int, str]
    type: int
        
@dataclass
class Item:        
    cost: int
    image: int
    id: str

class ShopData:
    
    last_reset_date: datetime
    background_stock: list[DictItem]
    treasure_stock: list[DictItem]
    stock_price: float
    stock_value: float
    motd: int
    
    async def setup_shop(self, data: dict):
        
        backgrounds = data['backgrounds']
        treasures = data['treasures']
        
        self.last_reset_date: datetime = datetime.strptime(data['last_reset_date'], "%Y-%m-%d %H:%M:%S")
        
        self.background_stock: list[DictItem] = []
        
        all_bgs = await fetch_background('all')
        
        for nid in backgrounds:
            
            bg = all_bgs[nid]
            
            if bg['type'] == 0:
                continue
            
            self.background_stock.append(DictItem(nid=nid, **bg))
            
        self.treasure_stock: list[DictItem] = []
        
        all_treasures = await fetch_treasure('all')
            
        for nid in treasures:
            
            treasure = all_treasures[nid]
            
            treasure["image"] = int(treasure["image"])
            self.treasure_stock.append(DictItem(nid=nid, type=0, **treasure))
        
        self.stock_price = data['stock_price']
        self.stock_value = data['stock_value']
        self.motd = data['motd']
        
        return self

async def fetch_shop_data():
    
    data: str = await fetch_shop()
     
    shop_data = ShopData()
    
    return await shop_data.setup_shop(data)

async def fetch_shop():
    async with aiofiles.open('bot/data/shop.json', 'r') as f:
        strdata = await f.read()
    
    return json.loads(strdata)

async def update_shop(shop_data: dict):
    async with aiofiles.open('bot/data/shop.json', 'w') as f:
        await f.write(json.dumps(shop_data, indent=4))

async def reset_shop_data(guild_id: int):
    
    data: dict = await fetch_shop()
    
    unparsed_backgrounds = await fetch_background('all')
    
    backgrounds = [bg for bg in unparsed_backgrounds if unparsed_backgrounds[bg]['type'] != 0]
        
    treasures = await fetch_treasure('all')
    motds = await loc(guild_id, 'Shop', 'MainShop', 'motds')
    
    data['backgrounds'] = []
    data['treasures'] = []
    
    n_backgrounds = random.sample(backgrounds, 3)
    n_treasures = random.sample(list(treasures.keys()), 3)
    
    data['backgrounds'] = n_backgrounds
    data['treasures'] = n_treasures
    data['motd'] = random.randint(0, len(motds) - 1)
    
    now = datetime.now()
    
    data['last_reset_date'] = datetime.strftime(datetime(now.year, now.month, now.day, hour=0, minute=0, second=0), '%Y-%m-%d %H:%M:%S')
    
    is_positive = random.choice([True, False])
    
    if data['stock_price'] < 0.5:
        is_positive = True
    
    if data['stock_price'] > 1.5:
        is_positive = False
    
    if is_positive:
        data['stock_value'] = round(random.uniform(0.3, 0.7), 1)
    else:
        data['stock_value'] = round(random.uniform(-0.3, -0.7), 1)    
    
    price_change = data['stock_price'] + data['stock_value']
    
    data['stock_price'] = round(min(2, max(0.2, price_change)), 1)
    
    await update_shop(data)
    
    shop_data = ShopData()
    
    return await shop_data.setup_shop(data)