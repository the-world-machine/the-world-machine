from collections import OrderedDict
import aiohttp

api_url = 'https://api.npoint.io/6940a9826da1e0473197' # If you see this, you can use this endpoint too!

async def fetch_item(item_type: str, item_index: int = -1) -> dict:
    '''
    Fetches item data from the API.
    
    Set item_index to -1 to get all items.
    
    item_type: str
    item_index: int (-1 by default)
    '''
    async with aiohttp.ClientSession() as session:
        if item_index == -1:
            async with session.get(f'{api_url}/items/{item_type}') as resp:
                if resp.status == 200:
                    return await resp.json()
        else:
            async with session.get(f'{api_url}/items/{item_type}/{item_index}') as resp:
                if resp.status == 200:
                    return await resp.json()

async def fetch_treasure(treasure_id: str):
    '''
    Fetches treasure data from the API.
    
    Set treasure_id to 'all' to get all treasures.
    
    treasure_id: str
    '''
    
    async with aiohttp.ClientSession() as session:
        if treasure_id == 'all':
            async with session.get(f'{api_url}/treasures') as resp:
                if resp.status == 200:
                    return await resp.json()
        else:
            async with session.get(f'{api_url}/treasures/{treasure_id}') as resp:
                if resp.status == 200:
                    return await resp.json()
                
async def fetch_background(background_id: str):
    '''
    Fetches background data from the API.
    
    Set background_id to 'all' to get all backgrounds.
    
    background_id: str
    '''
    
    async with aiohttp.ClientSession() as session:
        if background_id == 'all':
            async with session.get(f'{api_url}/backgrounds') as resp:
                if resp.status == 200:
                    return await resp.json()
        else:
            async with session.get(f'{api_url}/backgrounds/{background_id}') as resp:
                if resp.status == 200:
                    return await resp.json()

async def fetch_badge(badge_id: str):
    '''
    Fetches badge data from the API.
    
    Set badge_id to 'all' to get all badges.
    
    badge_id: str
    '''
    
    async with aiohttp.ClientSession() as session:
        if badge_id == 'all':
            async with session.get(f'{api_url}/badges') as resp:
                if resp.status == 200:
                    data = await resp.json()
        else:
            async with session.get(f'{api_url}/badges/{badge_id}') as resp:
                if resp.status == 200:
                    data = await resp.json()
                    
    return OrderedDict(sorted(data.items(), key=lambda x: x[1]['id']))