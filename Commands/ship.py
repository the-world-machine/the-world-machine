import random

from interactions import *

import Utilities.bot_icons as icons
from Utilities.fancysend import *
from Utilities.text_generation import generate_text


class Command(Extension):

    @slash_command(description="Ship two people together.")
    @slash_option(name="who", description="First person. Can be a user.", opt_type=OptionType.STRING, required=True)
    @slash_option(name="what", description="Second person. Can be a user.", opt_type=OptionType.STRING, required=True)
    async def ship(self, ctx: SlashContext, who: str, what: str):

        msg = await fancy_message(ctx, f"[ Coming up with ship name... {icons.loading()} ]")

        if '<' in who:
            parsed_id = who.strip('<@>')
            user = await self.bot.fetch_user(int(parsed_id))

            who = user.display_name
        if '<' in what:
            parsed_id = what.strip('<@>')
            user = await self.bot.fetch_user(int(parsed_id))

            what = user.display_name

        if who == what:
            await msg.delete()
            return await fancy_message(ctx, "[ Do you need a hug? ]", color=0xff0000, ephemeral=True)

        seed = len(who) + len(what)
        random.seed(seed)

        love_percentage = random.randint(0, 100)

        name = await generate_text(f'Combine the names {who} and {what} together. Just the result please.')

        emoji = '💖'
        description = ''

        if love_percentage == 100:
            emoji = '💛'
            description = 'Perfect compatibility.'
        if love_percentage < 100:
            emoji = '💖'
            description = 'In love.'
        if love_percentage < 70:
            emoji = '❤'
            description = 'There\'s interest!'
        if love_percentage <= 50:
            emoji = '❓'
            description = 'Maybe?'
        if love_percentage < 30:
            emoji = '❌'
            description = 'No interest.'
        if love_percentage < 10:
            emoji = '💔'
            description = 'Not at all.'

        l_length = list("🤍🤍🤍🤍🤍")

        calc_length = round((love_percentage / 100) * len(l_length))

        i = 0
        for _ in l_length:
            if i < calc_length:
                l_length[i] = '❤'
            i += 1

        length = "".join(l_length)

        embed = Embed(
            title=name,
            description=f'Compatibility: **{love_percentage}%** {emoji}\n{length}',
            color=0xd72d42
        )

        embed.set_footer(text=description)

        await msg.edit(embeds=embed)