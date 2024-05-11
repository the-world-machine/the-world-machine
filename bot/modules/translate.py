from interactions import *
from config_loader import load_config
from utilities.fancy_send import *
from database import UserData

import deepl

translator = deepl.Translator(load_config('deepl'))

class TranslationModule(Extension):

    @message_context_menu(name='💡 Translate...')
    async def translate(self, ctx: ContextMenuContext):

        await ctx.defer(ephemeral=True)
        
        target: Message = ctx.target

        user_data: UserData = await UserData(target.author.id).fetch()
        
        target_language = user_data.translation_language
        
        content = target.content
        
        if target.embeds:
           content = f'{content}\n\n`EMBED:` {target.embeds[0].description}' 

        message: deepl.TextResult = translator.translate_text(content, target_lang=target_language)

        await ctx.send(message.text, ephemeral=True)