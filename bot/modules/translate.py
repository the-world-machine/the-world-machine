from interactions import *
from utilities.fancy_send import *
from database import UserData

from utilities.ai_text import generate_text


class Command(Extension):

    @message_context_menu(name='💡 Translate...')
    async def translate(self, ctx: ContextMenuContext):

        await ctx.defer(ephemeral=True)

        user_data = await UserData(ctx.target.author.id).fetch()
        
        target_language = user_data.translation_language
        
        content = ctx.target.content
        
        if ctx.target.embeds:
           content = f'{content}\n\n`EMBED:` {ctx.target.embeds[0].description}' 

        message = await generate_text(f'Translate this message "{ctx.target.content}" please do it in the context of a native {target_language} speaker.')
        message = message.strip('\n')
        message = message.strip('"')

        await ctx.send(message, ephemeral=True)