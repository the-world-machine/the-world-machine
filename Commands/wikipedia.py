from interactions import *
from Utilities.fancysend import fancy_message
import aiohttp
import json
import random


class Command(Extension):

    @slash_command(description='A random wikipedia article.')
    async def random_wikipedia(self, ctx: SlashContext):
        async with aiohttp.ClientSession() as session:
            async with session.get(f'https://en.wikipedia.org/api/rest_v1/page/random/summary') as resp:
                if resp.status == 200:
                    get_search = await resp.json()

                    result = get_search['content_urls']['desktop']['page']

                    await fancy_message(ctx, f'[ [Here]({result}) is your random wikipedia article. ]')

    @slash_command(description='Search Wikipedia.')
    @slash_option(description='Search for a wikipedia article.', autocomplete=True, name='search', opt_type=OptionType.STRING, required=True)
    async def wikipedia(self, ctx: SlashContext, search: str):

        lang = 'en'

        if random.randint(0, 100) == 1:
            lang = 'fr'

        async with aiohttp.ClientSession() as session:
            async with session.get(
                    f'https://{lang}.wikipedia.org/w/api.php?format=json&action=query&prop=extracts&exintro=&explaintext=&titles={search}') as resp:
                if resp.status == 200:

                    get_search = await resp.json()

                    result: json = get_search['query']['pages']
                    key = list(result.keys())
                    result = result[key[0]]

                    content = ''
                    title = ''
                    url = ''
                    color = 0x8b00cc

                    try:
                        title = result['title']
                        content = result['extract']
                        url = f'https://{lang}.wikipedia.org/w/index.php?curid={result["pageid"]}'
                    except:
                        pass

                    if len(content) == 0:
                        title = search
                        content = 'Your search unfortunately came up with nothing'
                        url = 'https://en.wikipedia.org/wiki/OneShot'
                        color = 0xff0000

                    embed = Embed(
                        title=title,
                        description=content[0:4000] + '...',
                        url=url,
                        color=color
                    )

                    await ctx.send(embeds=embed)

    @wikipedia.autocomplete('search')
    async def autocomplete(self, ctx, text: str = 'OneShot'):  # teehee
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    f'https://en.wikipedia.org/w/api.php?action=opensearch&format=json&search={text}&formatversion=2') as resp:
                if resp.status == 200:
                    get_search = await resp.json()

                    result = get_search[1][:24]

                    await ctx.send(result)

    @slash_command(description='bogus')
    async def amogus(self, ctx: SlashContext):
        await ctx.send(
            'https://media.discordapp.net/attachments/868336598067056690/958829667513667584/1c708022-7898-4121-9968-0f0d24b8f986-1.gif')