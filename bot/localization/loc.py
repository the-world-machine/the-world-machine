from typing import Union
from yaml import safe_load
import utilities.bot_icons as icons

languages = {}
            
def fetch_language(locale: str):
    
    locale_value = locale
    
    if '_' in locale:
        l_prefix = locale.split('_')[0] # Create prefix for locale, for example en_UK and en_US becomes en_.

        if locale.startswith(l_prefix):
            locale_value = l_prefix + '_#'
    
    with open(f'bot/localization/locales/{locale_value}.yaml', 'r') as f:
        return safe_load(f)
    
def assign_variables(result: str, **variables: str):
    
    general_icons = {
        '&wool_icon': icons.icon_wool,
        '&loading_icon': icons.icon_loading
    }
    
    for name, icon in general_icons.items():
        result = result.replace(name, icon)
    
    for name, data in variables.items():
        result = result.replace(f'&{name}', data)
        
    return result    

def l(locale: str, localization_path: str, **variables: str) -> Union[str, list[str], dict]:
    
    value = fetch_language(locale)

    parsed_path = localization_path.split('.')
    
    # Get the values for the specified category and value
    for path in parsed_path:
        
        try:
            value = value[path]
        except:
            return f'`{localization_path}` is not a valid localization path.'
    
    result = value
    
    return assign_variables(result, **variables)

def fnum(num: int) -> str:
    return f'{num:>,}'