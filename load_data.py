import aiofiles
import json


def load_config(name: str) -> str:
    with open(f'Data/config.json', 'r') as f:
        raw_dict = f.read()

    return json.loads(raw_dict)[name]


def localization(name: str, *variables) -> str:
    with open(f'Data/localization.json', 'r') as f:
        raw_dict = f.read()

    template = json.loads(raw_dict)[name]

    return template % variables
