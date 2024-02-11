import os
import interactions

files = [f for f in os.listdir('bot/modules') if f != '__pycache__']
modules = [f.replace('.py', '') for f in files]

def load_commands(client: interactions.Client):

    # Load each module using the client.load method
    [client.load_extension(f"modules.{module}") for module in modules]

    print(f"Loaded {len(modules)} modules.")
    
