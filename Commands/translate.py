from interactions import *
from Utilities.fancysend import *
from database import Database

from Utilities.text_generation import generate_text


class Command(Extension):

    @message_context_menu(name='💡 Translate...')
    async def translate(self, ctx: ContextMenuContext):

        await ctx.defer(ephemeral=True)

        target_language = await Database.fetch('UserData', ctx.author.id, 'translation_language')

        message = await generate_text(f'Translate this message "{ctx.target.content}" please do it in the context of a native {target_language} speaker.')
        message = message.strip('\n')
        message = message.strip('"')

        embed = Embed(
            description=f'Translation to {target_language}```{message}```',
            color=0x8100bf
        )
        await ctx.send(embeds=embed, ephemeral=True)