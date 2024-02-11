import aiofiles
import json
import yaml

def load_config(*args: str) -> any:
    with open('bot/data/config.yaml', 'r') as f:
        data = yaml.safe_load(f)

    # Traverse the YAML structure based on the provided arguments
    for arg in args:
        if arg in data:
            data = data[arg]
        else:
            # Handle the case where the specified key is not found
            raise KeyError(f"Key '{arg}' not found in the configuration.")

    return data