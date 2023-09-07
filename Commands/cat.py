from interactions import *
from Utilities.fancysend import *

import random
import requests
import json


class Command(Extension):

    @slash_command(description="Get a random picture of a cat.")
    async def cat(self, ctx: SlashContext):

        embed = Embed(
            title='You found...',
            color=0x7e00b8
        )

        if random.randint(0, 100) == 67:
            embed.description = 'Niko!'
            embed.set_image(
                'https://cdn.discordapp.com/attachments/1028022857877422120/1075445796113219694/ezgif.com-gif-maker_1.gif')
            embed.set_footer('A 1 in 100 chance! Lucky!')
            return await ctx.send(embed=embed)

        data = requests.get('https://api.thecatapi.com/v1/images/search')

        json_data = json.loads(data.text)

        image = json_data[0]['url']

        embed.description = 'a cat!'
        embed.set_image(image)
        return await ctx.send(embed=embed)
