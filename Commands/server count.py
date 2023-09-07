from interactions import *
from Utilities.fancysend import fancy_message


class Command(Extension):
    @slash_command(description='View how many servers the bot is in.')
    async def server_count(self, ctx: SlashContext):

        await fancy_message(ctx, f'[ I am in **{len(self.client.guilds)}** servers. ]')