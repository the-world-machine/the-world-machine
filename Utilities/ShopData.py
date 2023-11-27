import aiofiles
import json
from database import Database
import json

class Background:
    
    def __init__(self, background: dict):
        self.cost: int = background['cost']
        self.type_: str = background['type']
        self.image: str = background['image']
        self.nid: str = background['name']
        
class Item:
    
    def __init__(self, item: dict):
        self.cost: int = item['price']
        self.image: str = item['image']
        self.nid: str = item['nid']

class Shop_:
    
    def __init__(self, data: dict, backgrounds: dict, items: dict):
        self.last_reset_date: int = data['last_reset_date']
        
        self.background_stock: list[Background] = []
        
        for bg in json.loads(data['backgrounds']):
            self.background_stock.append(Background(backgrounds[bg]))
            
        self.treasure_stock: list[Item] = []
            
        for t in json.loads(data['treasure']):
            self.treasure_stock.append(Item(items[t]))
        
        self.stock_price: int = data['stock_price']
        self.stock_value: float = data['stock_value']
        self.motd: str = data['motd']

async def fetch_shop_data():
    
    data: str = await Database.fetch_shop_data(),
    backgrounds: dict = await Database.get_items('Backgrounds'),
    items: dict = await Database.get_items('Treasures')
    
    
    return Shop_(data[0], backgrounds[0], items)