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

        if not can_ask:
            return await fancy_message(ctx, "[ You cannot ask anymore questions, you have reached your limit for today! ]", ephemeral=True, color=0xff0000)

        thinking_embed = Embed(
            color=0x8b00cc
        )

        thinking_embed.description = f'Thinking how to answer... {bot_icons.loading()}'
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

        twm = 'https://cdn.discordapp.com/attachments/1028022857877422120/1139694391833935892/1.png'

        if emotion == 'Happy':
            twm = 'https://cdn.discordapp.com/attachments/1028022857877422120/1139694392064606379/2.png'
        if emotion == 'Excited':
            twm = 'https://cdn.discordapp.com/attachments/1028022857877422120/1139694828502909040/8.png'
        if emotion == 'Angry':
            twm = 'https://cdn.discordapp.com/attachments/1028022857877422120/1139694392366608475/3.png'
        if emotion == 'Confused':
            twm = 'https://cdn.discordapp.com/attachments/1028022857877422120/1139694393150947489/6.png'
        if emotion == 'Sad':
            twm = 'https://cdn.discordapp.com/attachments/1028022857877422120/1139695873085931601/9.png'
        if emotion == 'Tired':
            twm = 'https://cdn.discordapp.com/attachments/1028022857877422120/1139694393415172237/7.png'
        if emotion == 'Disgusted':
            twm = 'https://cdn.discordapp.com/attachments/1028022857877422120/1139695850965180496/10.png'

        final_embed = Embed(
            color=0x8b00cc
        )

        final_embed.set_thumbnail(url=twm)
        final_embed.set_author(name=question[:4000], icon_url=ctx.author.avatar_url)
        final_embed.set_footer(text=f'You have {limit} questions left for today.')

        await ctx.delete()

        final_embed.description = f'[ {response} ]'

        await increment_value(ctx, 'times_asked', ctx.user)

        await ctx.channel.send(embed=final_embed)

    async def check(self, uid: int):

        current_limit = await database.get('user_data', uid, 'gpt_limit')
        timestamp_str = await database.get('user_data', uid, 'gpt_timestamp')
        timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S.%f')
        now = datetime.now()

        if now < timestamp:
            if current_limit <= 0:
                return False, current_limit

            await database.set('user_data', 'gpt_limit', uid, current_limit - 1)
            return True, current_limit - 1

        new_day = now + timedelta(days=1)
        await database.set('user_data', 'gpt_timestamp', uid, new_day.strftime('%Y-%m-%d %H:%M:%S.%f'))
        await database.set('user_data', 'gpt_limit', uid, 14)
        return True, 14
