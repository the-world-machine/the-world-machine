from interactions import *
from utilities.fancy_send import *
import utilities.profile.badge_manager as badge_manager
from bot.utilities.emojis import *


class _Module(Extension):

    @slash_command(description="This is a Boilerplate Command.")
    @slash_option(name="option_name", description="This is a Boilerplate Option.", opt_type=OptionType.STRING)
    async def hello(self, ctx: SlashContext, option_name: str):
        await fancy_message(ctx, "Hello, " + option_name)
