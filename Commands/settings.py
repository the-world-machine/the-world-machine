from interactions import *
import database as db
from Utilities.fancysend import fancy_message


class Command(Extension):
    @slash_command(description="Change settings for yourself.")
    async def user_settings(self, ctx: SlashContext):
        pass

    @slash_command(description="Change settings for the server you are on.")
    async def server_settings(self, ctx: SlashContext):
        can_manage_channels = await ctx.author.has_permissions(Permissions.MANAGE_CHANNELS)

        if not can_manage_channels:
            return await fancy_message(ctx,
                                       '[ Sorry, you need the ``MANAGE_CHANNELS`` permission in order to use this command. ]',
                                       ephemeral=True, color=0xff060d)

    @user_settings.subcommand(sub_cmd_description='Change whether you want notifications to appear when you unlock a badge.')
    @slash_option(description='DEFAULT: True', name='value', opt_type=OptionType.BOOLEAN, required=True)
    async def badge_notifications(self, ctx: SlashContext, value: bool):

        db.update('user_data', 'unlock_notifications', ctx.user.id, value)
        await fancy_message(ctx, f'[ Successfully set badge notifications to ``{value}``. ]', ephemeral=True)

    @user_settings.subcommand(sub_cmd_description='Change the language you wish to translate to.')
    @slash_option(description='DEFAULT: English', max_length=30, name='language', opt_type=OptionType.STRING, required=True)
    async def translate_language(self, ctx: SlashContext, language: str):

        db.update('user_data', 'translation_language', ctx.user.id, language)
        await fancy_message(ctx, f'[ Successfully set translation language to ``{language}``. ]', ephemeral=True)

    @server_settings.subcommand(
        sub_cmd_description='The transmission channel to use to allow other servers to call. Leave blank to disable.')
    @slash_option(description='DEFAULT: NO CHANNEL SET', name='channel', opt_type=OptionType.CHANNEL)
    async def change_transmission_channel(self, ctx: SlashContext, channel):
        if channel is None:
            db.update('server_data', 'transmit_channel', ctx.guild_id, None)
            return await fancy_message(ctx, '[ Successfully disabled transmission calls. ]', ephemeral=True)

        db.update('server_data', 'transmit_channel', ctx.guild_id, int(channel.id))
        return await fancy_message(ctx, f'[ Successfully allowed other servers to call to {channel.mention}. ]', ephemeral=True)