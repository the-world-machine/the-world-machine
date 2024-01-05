from datetime import datetime, timedelta
from interactions import *
from Utilities.fancysend import *
from Utilities.badge_manager import increment_value
import Utilities.bot_icons as bot_icons
import Utilities.text_generation as ai
from Utilities.DatabaseTypes import fetch_user


class Command(Extension):

    @slash_command(description="Ask The World Machine anything.")
    @slash_option(name="question", description="The question to ask.", opt_type=OptionType.STRING, required=True)
    async def ask(self, ctx: SlashContext, question: str):

        can_ask, limit = await self.check(ctx.author.id)

        if not can_ask and self.bot.user.id != 1028058097383641118:
            return await fancy_message(ctx, "[ You cannot ask anymore questions, you have reached your limit for today! ]", ephemeral=True, color=0xff0000)

        thinking_embed = Embed(
            color=0x8b00cc
        )

        thinking_embed.description = f'*Thinking how to answer...* 1/2 {bot_icons.icon_loading}'
        thinking_embed.set_footer(text=f'You have {limit} questions left for today.')

        msg = await ctx.send(embed=thinking_embed)

        response = await ai.chat(ctx, question)

        emotion_embed = Embed(
            color=0x8b00cc
        )

        emotion_embed.description = f'*Thinking how to answer...* 2/2 {bot_icons.icon_loading}'
        emotion_embed.set_footer(text=f'You have {limit} questions left for today.')

        msg = await msg.edit(embed=emotion_embed)

        emotion = await ai.generate_text(f'{response}\n\nFrom a list of possible answers, choose the best fitting emotion: Happy Sad Excited Disgusted Tired Angry Confused.')

        twm = 'https://cdn.discordapp.com/emojis/1023573456664662066.webp?size=128&quality=lossless'

        if emotion == 'Happy':
            twm = 'https://cdn.discordapp.com/emojis/1023573455456698368.webp?size=128&quality=lossless'
        if emotion == 'Excited':
            twm = 'https://cdn.discordapp.com/emojis/1023573458296246333.webp?size=128&quality=lossless'
        if emotion == 'Angry':
            twm = 'https://cdn.discordapp.com/emojis/1023573452944322560.webp?size=128&quality=lossless'
        if emotion == 'Confused':
            twm = 'https://cdn.discordapp.com/emojis/1023573456664662066.webp?size=128&quality=lossless'
        if emotion == 'Sad':
            twm = 'https://cdn.discordapp.com/emojis/1023573454307463338.webp?size=128&quality=lossless'
        if emotion == 'Tired':
            twm = 'https://cdn.discordapp.com/emojis/1023573452944322560.webp?size=128&quality=lossless'
        if emotion == 'Disgusted':
            twm = 'https://cdn.discordapp.com/emojis/1023573452944322560.webp?size=128&quality=lossless'

        final_embed = Embed(
            color=0x8b00cc
        )

        final_embed.set_thumbnail(url=twm)

        final_embed.description = f'[ {response} ]'
        
        final_embed.set_author(name=question[0:250])

        await increment_value(ctx, 'times_asked', 1, ctx.user)

        await msg.edit(embed=final_embed)

    async def check(self, uid: int):

        user = await fetch_user(uid)
        now = datetime.now()

        if now < user.last_asked:
            if user.ask_limit <= 0:
                return False, user.ask_limit

            await user.update(ask_limit=user.ask_limit - 1)
            return True, user.ask_limit

        new_day = now + timedelta(days=1)
        
        await user.update(
            last_asked = new_day,
            ask_limit = 14
        )
        
        return True, 14
