from genericpath import exists
from typing import Union
from yaml import safe_load
import io
import utilities.emojis as emojis
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
        with open(f'bot/localization/locales/en-#.yaml', 'r', encoding='utf-8') as f:
            return safe_load(f)
    
def assign_variables(result: str, **variables: str):
    
    emoji_dict = {f'emoji:{name.replace("icon_", "")}': getattr(emojis, name) for name in dir(emojis)}
    
    for name, data in {**variables, **emoji_dict}.items():
        
        if type(data) != str:
            data = fnum(data)
        
        result = result.replace(f'[{name}]', data)
        
    return result

def fnum(num: int) -> str:
    return f'{num:>,}'