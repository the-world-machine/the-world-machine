from interactions import *
from config_loader import load_config
from utilities.fancy_send import *
from database import UserData

import deepl

translator = deepl.Translator(load_config('deepl'))

class Command(Extension):

    @message_context_menu(name='💡 Translate...')
    async def translate(self, ctx: ContextMenuContext):

        await ctx.defer(ephemeral=True)

        user_data = await UserData(ctx.target.author.id).fetch()
        
        target_language = user_data.translation_language
        
        content = ctx.target.content
        
        if ctx.target.embeds:
           content = f'{content}\n\n`EMBED:` {ctx.target.embeds[0].description}' 

        message = translator.translate_text(content, target_lang=target_language)

        await ctx.send(message.text, ephemeral=True)