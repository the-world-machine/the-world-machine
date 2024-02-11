import aiofiles
import json


def load_config(name: str) -> str:
    with open(f'bot/data/config.json', 'r') as f:
        raw_dict = f.read()

    return json.loads(raw_dict)[name]