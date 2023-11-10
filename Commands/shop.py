from interactions import *

from Utilities.fancysend import *


class Command(Extension):

    @slash_command(description="Shop command.")
    async def shop(self, ctx: SlashContext):
        await fancy_message(ctx, "[ Hello! This shop command has been moved to: https://www.theworldmachine.xyz/shop ]",
                            ephemeral=True)
