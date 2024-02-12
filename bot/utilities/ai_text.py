import openai
import re
from interactions import SlashContext, Message
from config_loader import *

openai.api_key = load_config('open-ai')


async def chat(bot_id: int, message: Message, limit: int):
    system_prompt = ''

    with open('bot/data/askprompt.txt', 'r') as f:
        system_prompt = f.read()
        
    system_prompt = system_prompt.replace('+server', message.guild.name)
    system_prompt = system_prompt.replace('+limit', str(limit))
        
    messages = await message.channel.fetch_messages(limit=10)
    
    formatted_messages = []
    
    async def format_message(msg: Message):
        'format message in order to have it be acceptable for the AI to read.'
        
        if len(msg.embeds) > 0:
            content = f'{msg.content} {msg.embeds[0].description}'
        else:
            content = msg.content
            
        content = content.replace(f'<@{bot_id}>', '')
        
        return content
    
    messages.insert(0, message)
    
    for i, message in enumerate(messages):
        
        if message.author.bot:
            if message.embeds:
                continue
        
        content = await format_message(message)
        
        referenced_message = await message.fetch_referenced_message()
            
        if referenced_message is not None:
            referenced_message_content = await format_message(referenced_message)
            
            indicator =  f'In response to {referenced_message.author.display_name}\'s message ({referenced_message_content})\n\n{message.author.display_name} has said: '
        else:    
            indicator = f'{message.author.display_name} has said: '
        
        formatted_messages.append({'role': 'user', 'content': indicator + content})
            
    formatted_messages.append({"role": "system", "content": system_prompt})
    
    formatted_messages.reverse()
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=formatted_messages,
        temperature=0.8,
        top_p=0.3,
        frequency_penalty=0.8,
        presence_penalty=0.7,
        max_tokens=1000
    )

    return response['choices'][0]['message']['content']


async def generate_text(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.1
    )

    return response['choices'][0]['message']['content']


async def translate(text):
    
    response = openai.Completion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": text}
        ],
        temperature=0.1,
        top_p=0.1,
        frequency_penalty=0.1,
        presence_penalty=0.1,
    )
    
    return response['choices'][0]['message']['content']
