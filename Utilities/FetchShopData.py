import aiofiles
import json

async def fetch_shop_data():
    async with aiofiles.open('Data/shop_items.json', 'r') as f:
        data = await f.read()

    return json.loads(data)