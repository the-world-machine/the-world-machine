from datetime import datetime
import random
import aiofiles
import json

from interactions import SlashContext
from database import Database
from Localization.Localization import loc
import json

class Background:
    
    def __init__(self, background: dict):
        self.id_: int = background['p_key'] - 1
        self.cost: int = background['cost']
        self.type: str = background['type']
        self.image: str = background['image']
        self.nid: str = background['name']
        
class Item:
    
    def __init__(self, item: dict):
        self.cost: int = item['price']
        self.image: str = item['image']
        self.nid: str = item['nid']
        self.id_: int = item['p_key'] - 1
        self.type: str = item.get('type', 'any')

class ShopData:
    
    def __init__(self, data: dict, backgrounds: dict, items: dict):
        self.last_reset_date: datetime = data['last_reset_date']
        
        self.background_stock: list[Background] = []
        
        for bg in json.loads(data['backgrounds']):
            self.background_stock.append(Background(backgrounds[bg]))
            
        self.treasure_stock: list[Item] = []
            
        for t in json.loads(data['treasure']):
            self.treasure_stock.append(Item(items[t]))
        
        self.stock_price: int = data['stock_price']
        self.stock_value: float = data['stock_value']
        self.motd: int = data['motd']

async def fetch_shop_data():
    
    data: str = await Database.fetch_shop_data()
    backgrounds: dict = await Database.get_items('Backgrounds')
    items: dict = await Database.get_items('Treasures')
     
    return ShopData(data, backgrounds, items)

async def reset_shop_data(guild_id: int):
    
    data: dict = await Database.fetch_shop_data()
    
    bgs = await Database.get_items('Backgrounds')
    trs = await Database.get_items('Treasures')
    motds = await loc(guild_id, 'Shop', 'MainShop', 'motds')
    
    backgrounds = range(6, len(bgs))
    treasures = range(0, len(trs))
    
    n_backgrounds = random.sample(backgrounds, 3)
    n_treasures = random.sample(treasures, 3)
    
    data['backgrounds'] = json.dumps(n_backgrounds)
    data['treasure'] = json.dumps(n_treasures)
    data['motd'] = random.randint(0, len(motds) - 1)
    
    now = datetime.now()
    
    data['last_reset_date'] = datetime(now.year, now.month, now.day, hour=0, minute=0, second=0)
    
    data['stock_value'] = round(random.uniform(-0.5, 0.5), 1)
    price_change = data['stock_price'] + data['stock_value']
    
    data['stock_price'] = min(2, max(0.2, price_change))
    
    await Database.update('shop_data', 'stock_price', 0, data['stock_price'])
    await Database.update('shop_data', 'stock_value', 0, data['stock_value'])
    await Database.update('shop_data', 'last_reset_date', 0, data['last_reset_date'])
    await Database.update('shop_data', 'backgrounds', 0, data['backgrounds'])
    await Database.update('shop_data', 'treasure', 0, data['treasure'])
    await Database.update('shop_data', 'motd', 0, data['motd'])
    
    return ShopData(data, bgs, trs)