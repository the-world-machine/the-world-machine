from interactions import *
import random


class Command(Extension):

    @slash_command(description='Roll a dice.')
    @slash_option(description='What sided dice to roll.', min_value=1, max_value=9999, name='sides', opt_type=OptionType.INTEGER, required=True)
    @slash_option(description='How many to roll.', min_value=1, max_value=10, name='amount', opt_type=OptionType.INTEGER)
    async def roll(self, ctx: SlashContext, sides: int, amount: int = 1):

        dice = random.randint(1, sides)

        if amount == 1:
            description = f'[ Rolled a **{dice}**. ]'
        else:
            text = ''
            previous_total = 0
            total = 0

            for num in range(amount):

                dice = random.randint(1, sides)

                if num == 0:
                    text = f'**{dice}**'

                    previous_total = dice
                    continue

                text = f'{text}, **{dice}**'

                total = previous_total + dice

                previous_total = total

            description = f'[ Rolled a {text}, totaling at **{total}**. ]'

        embed = Embed(title=f'Rolling d{sides}...', description=description, color=0x8b00cc)
        embed.set_thumbnail('https://cdn.discordapp.com/emojis/1026181557230256128.png?size=96&quality=lossless')

        await ctx.send(embeds=embed)
