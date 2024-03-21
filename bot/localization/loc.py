from genericpath import exists
from typing import Union
from yaml import safe_load
import io
import utilities.bot_icons as icons
from dataclasses import dataclass

languages = {}

@dataclass
class Localization:
    locale: str
    
    def l(self, localization_path: str, **variables: str) -> Union[str, list[str], dict]:
        value = fetch_language(self.locale)

        parsed_path = localization_path.split('.')
        
        # Get the values for the specified category and value
        for path in parsed_path:
            
            try:
                value = value[path]
            except:
                return f'`{localization_path}` is not a valid localization path.'
        
        result = value
        
        if type(result) == dict or type(result) == list:
            return result
        else:
            return assign_variables(result, **variables)
            
def fetch_language(locale: str):
    
    locale_value = locale
    
    if '-' in locale:
        l_prefix = locale.split('-')[0] # Create prefix for locale, for example en_UK and en_US becomes en.

        if locale.startswith(l_prefix):
            locale_value = l_prefix + '-#'
    
    if exists(f'bot/localization/locales/{locale_value}.yaml'):
        with open(f'bot/localization/locales/{locale_value}.yaml', 'r', encoding='utf-8') as f:
            return safe_load(f)
    else:
        
        print(f'Failed to load localization for {locale}.')
        
        with open(f'bot/localization/locales/en-#.yaml', 'r', encoding='utf-8') as f:
            return safe_load(f)
    
def assign_variables(result: str, **variables: str):
    
    general_icons = {
        'wool_icon': icons.icon_wool,
        'loading_icon': icons.icon_loading
    }
    
    for name, data in {**variables, **general_icons}.items():
        
        if type(data) != str:
            
            how_big_is_this_number = len(str(data))
            
            if how_big_is_this_number < 17:
                data = fnum(data)
            else:
                # A bit hacky, but if the number is really big, then it's most likely a snowflake.
                data = f'<:icon:{data}>'
        
        result = result.replace(f'[{name}]', data)
        
    return result

def fnum(num: int) -> str:
    return f'{num:>,}'