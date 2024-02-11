from interactions import *
from utilities.fancy_send import fancy_message
import aiohttp

class Command(Extension):
    @slash_command(description='View how many servers the bot is in.')
    async def server_count(self, ctx: SlashContext):

        await fancy_message(ctx, f'[ I am in **{len(self.client.guilds)}** servers. ]')
        
    @slash_command(description='View the bot\'s status.')
    async def bot_status(self, ctx: SlashContext):
        
        embed = Embed()
        
        embed.add_field('♥️ Heartbeat', str(self.bot.heart))
        
    @slash_command(description='A random wikipedia article.')
    async def random_wikipedia(self, ctx: SlashContext):
        async with aiohttp.ClientSession() as session:
            async with session.get(f'https://en.wikipedia.org/api/rest_v1/page/random/summary') as resp:
                if resp.status == 200:
                    get_search = await resp.json()

                    result = get_search['content_urls']['desktop']['page']

                    await fancy_message(ctx, f'[ [Here]({result}) is your random wikipedia article. It\'s about {get_search["title"]}... I think... ]')

    @slash_command(description='bogus')
    async def amogus(self, ctx: SlashContext):
        await ctx.send(
            'https://media.discordapp.net/attachments/868336598067056690/958829667513667584/1c708022-7898-4121-9968-0f0d24b8f986-1.gif')
        
    