from database import Database
from typing import Union
import importlib

language_cache = {}

async def get_lang(guild_id: int):
    server_language: str = await Database.fetch('server_data', 'bot_language', guild_id)

    if server_language in language_cache:
        return language_cache[server_language]

    language_module = importlib.import_module(f'Localization.{server_language}')
    
    data = getattr(language_module, 'text')
    
    language_cache[server_language] = data
    return data

async def loc(guild_id: int, *args: str, values: dict = {}) -> Union[str, list[str], dict]:
    t = await get_lang(guild_id)

    # Call the 'text' function with the 'l_args' dictionary
    text: dict = t(values)

    # Get the values for the specified category and value
    for arg in args:
        text = text.get(arg, None)
        
        if text is None:
            break

    if text is None:
        result = f'⚠️ ``{args}`` is not localized.'
    else:
        result = text
    
    return result

def l_num(num: int) -> str:
    return f'{num:>,}'