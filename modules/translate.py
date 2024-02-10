from interactions import *
from Utilities.fancysend import *
from database import UserData

from Utilities.ai_text import generate_text


class Command(Extension):

    @message_context_menu(name='💡 Translate...')
    async def translate(self, ctx: ContextMenuContext):

        await ctx.defer(ephemeral=True)

        user_data = await UserData(ctx.target.author.id).fetch()
        
        target_language = user_data.translation_language

        message = await generate_text(f'Translate this message "{ctx.target.content}" please do it in the context of a native {target_language} speaker.')
        message = message.strip('\n')
        message = message.strip('"')

        embed = Embed(
            description=f'Translation to {target_language}```{message}```',
            color=0x8100bf
        )
        await ctx.send(embeds=embed, ephemeral=True)