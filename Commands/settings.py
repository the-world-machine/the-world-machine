from interactions import *

from database import Database as db
from Utilities.fancysend import fancy_message


class Command(Extension):
    @slash_command(description="Change settings for yourself.")
    async def user_settings(self, ctx: SlashContext):
        await fancy_message(ctx, "[ Hello! This command has been moved to: https://www.theworldmachine.xyz/profile ]",
                            ephemeral=True)

    @slash_command(description="Change settings for the server you are on.")
    async def server_settings(self, ctx: SlashContext):
        pass


    @server_settings.subcommand(
        sub_cmd_description='The transmission channel to use to allow other servers to call. Leave blank to disable.')
    @slash_option(description='DEFAULT: NO CHANNEL SET', name='channel', opt_type=OptionType.CHANNEL)
    async def transmit_channel(self, ctx: SlashContext, channel):

        can_manage_channels = await ctx.author.has_permissions(Permissions.MANAGE_CHANNELS)

        if not can_manage_channels:
            return await fancy_message(ctx,
                                       '[ Sorry, you need the ``MANAGE_CHANNELS`` permission in order to use this command. ]',
                                       ephemeral=True, color=0xff060d)

        if channel is None:
            await db.update('server_data', 'transmit_channel', ctx.guild_id, None)
            return await fancy_message(ctx, '[ Successfully disabled transmission calls. ]', ephemeral=True)

        await db.update('server_data', 'transmit_channel', ctx.guild_id, int(channel.id))
        return await fancy_message(ctx, f'[ Successfully allowed other servers to call to {channel.mention}. ]',
                                   ephemeral=True)

    @server_settings.subcommand(
        sub_cmd_description="Disable/Enable receiving images when transmitting. All redacted images will be sent as [IMAGE].")
    @slash_option(description='DEFAULT: TRUE', name='value', opt_type=OptionType.BOOLEAN, required=True)
    async def transmit_images(self, ctx: SlashContext, value):

        can_manage_channels = await ctx.author.has_permissions(Permissions.MANAGE_CHANNELS)

        if not can_manage_channels:
            return await fancy_message(ctx,
                                       '[ Sorry, you need the ``MANAGE_CHANNELS`` permission in order to use this command. ]',
                                       ephemeral=True, color=0xff060d)

        await db.update('server_data', 'transmit_images', ctx.guild_id, value)

        if value:
            return await fancy_message(ctx, '[ Successfully enabled transmission images. ]', ephemeral=True)
        else:
            return await fancy_message(ctx, '[ Successfully disabled transmission images. ]', ephemeral=True)

    @server_settings.subcommand(
        sub_cmd_description="Disable/Enable whether transmission receivers are shown Oneshot characters instead of users.")
    @slash_option(description='DEFAULT: FALSE', name='value', opt_type=OptionType.BOOLEAN, required=True)
    async def transmit_anonymous(self, ctx: SlashContext, value):

        can_manage_channels = await ctx.author.has_permissions(Permissions.MANAGE_CHANNELS)

        if not can_manage_channels:
            return await fancy_message(ctx,
                                       '[ Sorry, you need the ``MANAGE_CHANNELS`` permission in order to use this command. ]',
                                       ephemeral=True, color=0xff060d)

        await db.update('server_data', 'transmit_anonymous', ctx.guild_id, value)

        if value:
            return await fancy_message(ctx, '[ Successfully enabled anonymous mode. ]', ephemeral=True)
        else:
            return await fancy_message(ctx, '[ Successfully disabled anonymous mode. ]', ephemeral=True)
