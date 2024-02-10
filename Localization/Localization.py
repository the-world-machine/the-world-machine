import database
from typing import Union
import importlib
import os

languages = {}

def load_languages():
    
    for file in os.listdir('Localization/lang'):
        if file.endswith('.py'):
            language = file.replace('.py', '')
            module = importlib.import_module(f'Localization.lang.{language}')
            
            languages[language] = module

async def get_lang(guild_id: int):
    
    server_data = await database.ServerData(guild_id).fetch()
    
    server_language: str = server_data.language

    language_module = importlib.reload(languages[server_language])
    
    data = getattr(language_module, 'text')
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