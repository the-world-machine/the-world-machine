from database import Database
from typing import Union
import importlib

async def get_lang(guild_id: int):
    server_language: str = await Database.fetch('server_data', 'bot_language', guild_id)

    # Import the language module
    language = importlib.import_module(f'Localization.{server_language}')
    
    # Reload the language (so any changes can get updated).
    language = importlib.reload(language)

    # Get the 'text' function from the language module
    return getattr(language, 'text')

async def loc(guild_id: int, *args: str, values: dict = {}) -> Union[str, list[str], dict]:
    try:
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
    
    except Exception as e:
        result = f'⚠️ Error: {str(e)}'
    
    return result

def l_num(num: int) -> str:
    return f'{num:,}'