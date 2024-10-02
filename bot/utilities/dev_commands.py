import json
import re
from interactions import Message, User
from utilities.shop.fetch_shop_data import reset_shop_data
from config_loader import load_config
import database
import ast

async def get_collection(collection: str, _id: str):
    key_to_collection: dict[str, database.Collection] = {
        'user': database.UserData(_id),
        'nikogotchi': database.Nikogotchi(_id),
        'nikogotchi_old': database.NikogotchiData(_id),
        'server': database.ServerData(_id)
    }
    
    return key_to_collection[collection]

async def execute_dev_command(message: Message):
    
    if message.author.bot:
        return
    
    if not str(message.author.id) in load_config('dev-command-user-list'):
        return
    
    message_to_parse = message.content
    
    # This is not a valid command if brackets do not surround the message.
    if not (message_to_parse[0] == '[' or message_to_parse[-1] == ']'):
        return
    
    # Remove the brackets
    command_content = message_to_parse[1:-1].strip()
    
    # Split the command into parts
    command_parts = command_content.split()
    
    command_type = command_parts[0]
    
    if command_type == 'shop':
        
        action = command_parts[1]
        
        items = await database.fetch_items()
        shop = items['shop']
        
        if action == 'view':
            result = '```\n'
                
            for key in shop.keys():
                result += f'{key}: {str(shop[key])}\n'
                
            result += '```'
            
            await message.reply(result)
        
        if action == 'reset':
            await reset_shop_data('en-US')
            
            await message.reply(
                f'`[ Successfully reset shop. ]`'
            )
    
    if command_type == 'db':
        try:
            action = command_parts[1]
            
            if action == 'set':
                
                pattern = r'\{(?:[^{}]*|\{[^{}]*\})*\}'
                
                matches = re.findall(pattern, command_content)
                
                collection = command_parts[2]
                _id = command_parts[3]
                str_data = matches[0]

                data = json.loads(str_data)

                collection = await database.fetch_from_database(await get_collection(collection, _id))
                
                await collection.update(**data)
                
                await message.reply(
                    f'`[ Successfully updated value(s). ]`'
                )
                
            if action == 'view':
                collection = command_parts[2]
                _id = command_parts[3]
                value = command_parts[4]
                
                if collection == 'shop':
                    collection = await get_collection(collection, 0)
                else:
                    collection = await database.fetch_from_database(await get_collection(collection, _id))
                
                await message.reply(
                    f'`[ The value of {value} is {str(collection.__dict__[value])}. ]`'
                )
                
            if action == 'view_all':
                collection = command_parts[2]
                _id = command_parts[3]
                
                collection = await database.fetch_from_database(await get_collection(collection, _id))
                
                data = collection.__dict__
                
                result = '```\n'
                
                for key in data.keys():
                    result += f'{key}: {str(data[key])}\n'
                    
                result += '```'
                
                await message.reply(result)
                
                
            if action == 'wool':
                _id = command_parts[2]
                amount = int(command_parts[3])
                
                collection: database.UserData = await database.fetch_from_database(await get_collection('user', _id))
                
                await collection.manage_wool(amount)
                
                await message.reply(
                    f'`[ Successfully modified wool, updated value is now {collection.wool}. ]`'
                )
                
        except Exception as e:
            await message.reply(
                f'`[ Error with command. ({e}) ]`'
            )