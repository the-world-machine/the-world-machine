from datetime import datetime, timedelta
from interactions import *
from Utilities.fancysend import *
from Utilities.badge_manager import increment_value
import Utilities.bot_icons as bot_icons
import Utilities.text_generation as ai
import database


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

        thinking_embed.description = f'*Thinking how to answer...* {bot_icons.loading()}\n\n``{question}``'
        thinking_embed.set_author(name='⚠️ This command could potentially spoil OneShot!')
        thinking_embed.set_footer(text=f'You have {limit} questions left for today.')

        await ctx.send(embed=thinking_embed, ephemeral=True)

        response = await ai.chat(ctx, question)

        emotion_embed = Embed(
            color=0x8b00cc
        )

        emotion_embed.description = f'Thinking how I feel about this question... {bot_icons.loading()}'
        emotion_embed.set_author(name='⚠️ This command could potentially spoil OneShot!')
        emotion_embed.set_footer(text=f'You have {limit} questions left for today.')

        await ctx.edit(embed=emotion_embed)

        emotion = await ai.generate_text(f'{response} from a list of possible answers, choose the best fitting emotion: Happy Sad Excited Disgusted Tired Angry Confused.')

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
        final_embed.set_author(name=question[:255])
        final_embed.set_footer(text=f'Asked by {ctx.author.display_name} using /ask.', icon_url=ctx.author.avatar_url)

        await ctx.delete()

        final_embed.description = f'[ {response} ]'

        await increment_value(ctx, 'times_asked', ctx.user)

        await ctx.channel.send(embed=final_embed)

    async def check(self, uid: int):

        current_limit = database.get('user_data', uid, 'gpt_limit')
        timestamp_str = database.get('user_data', uid, 'gpt_timestamp')
        try:
            timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S.%f')
        except:
            timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')

        now = datetime.now()

        if now < timestamp:
            if current_limit <= 0:
                return False, current_limit

            database.update('user_data', 'gpt_limit', uid, current_limit - 1)
            return True, current_limit - 1

        new_day = now + timedelta(days=1)
        database.update('user_data', 'gpt_timestamp', uid, new_day.strftime('%Y-%m-%d %H:%M:%S.%f'))
        database.update('user_data', 'gpt_limit', uid, 14)
        return True, 14
