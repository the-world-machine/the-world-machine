import json
from interactions import *

import database as db
from utilities.fancy_send import fancy_message


class Command(Extension):
    @slash_command(description="Change settings for yourself.")
    async def user_settings(self, ctx: SlashContext):
        await fancy_message(ctx, "[ Hello! This command has been moved to: https://www.theworldmachine.xyz/profile ]",
                            ephemeral=True)

    @slash_command(description="Change settings for the server you are on.")
    async def server_settings(self, ctx: SlashContext):
        pass

    
    @slash_command(description="Base command for Transmission Settings.")
    async def transmission_settings(self, ctx: SlashContext):
        pass
    

    @transmission_settings.subcommand(
        sub_cmd_description='The transmission channel to use to allow other servers to call. Leave blank to disable.')
    @slash_default_member_permission(Permissions.MANAGE_GUILD)
    @slash_option(description='DEFAULT: NO CHANNEL SET', name='channel', opt_type=OptionType.CHANNEL)
    async def transmit_channel(self, ctx: SlashContext, channel: GuildText):
        
        server_data = await db.fetch_server_data(ctx.guild_id)

        if channel is None:
            await server_data.update(transmit_channel=None)
            return await fancy_message(ctx, '[ Successfully disabled transmission calls. ]', ephemeral=True)

        await server_data.update(transmit_channel=str(channel.id))
        return await fancy_message(ctx, f'[ Successfully allowed other servers to call to {channel.mention}. ]',
                                   ephemeral=True)

    @transmission_settings.subcommand(
        sub_cmd_description="Disable/Enable receiving images when transmitting. All redacted images will be sent as [IMAGE].")
    @slash_default_member_permission(Permissions.MANAGE_GUILD)
    @slash_option(description='DEFAULT: TRUE', name='value', opt_type=OptionType.BOOLEAN, required=True)
    async def transmit_images(self, ctx: SlashContext, value):
        
        server_data = await db.fetch_server_data(ctx.guild_id)

        await server_data.update(transmit_images=value)

        if value:
            return await fancy_message(ctx, '[ Successfully enabled transmission images. ]', ephemeral=True)
        else:
            return await fancy_message(ctx, '[ Successfully disabled transmission images. ]', ephemeral=True)

    @transmission_settings.subcommand(
        sub_cmd_description="Disable/Enable whether transmission receivers are shown Oneshot characters instead of users.")
    @slash_default_member_permission(Permissions.MANAGE_GUILD)
    @slash_option(description='DEFAULT: FALSE', name='value', opt_type=OptionType.BOOLEAN, required=True)
    async def transmit_anonymous(self, ctx: SlashContext, value):
        
        server_data = await db.fetch_server_data(ctx.guild_id)

        await server_data.update(transmit_anonymous=value)

        if value:
            return await fancy_message(ctx, '[ Successfully enabled anonymous mode. ]', ephemeral=True)
        else:
            return await fancy_message(ctx, '[ Successfully disabled anonymous mode. ]', ephemeral=True)
        
    @transmission_settings.subcommand(sub_cmd_description='Block a server from being able to call.')
    @slash_option(description='Server to block.', name='server', opt_type=OptionType.STRING, required=True, autocomplete=True)
    async def block_server(self, ctx: SlashContext, server: str):
        
        server_data = await db.fetch_server_data(ctx.guild_id)
        
        block_list = server_data.blocked_servers
        
        try:
            server_id = int(server)
        except ValueError:
            return await fancy_message(ctx, '[ Invalid server ID. ]', ephemeral=True)
        
        if server_id in block_list:
            block_list.remove(server_id)
            
            await server_data.update(blocked_servers=block_list)
            
            return await fancy_message(ctx, f'[ Successfully unblocked server `{server}`. ]', ephemeral=True)
        
        block_list.append(server_id)
        
        await server_data.update(blocked_servers=block_list)
        return await fancy_message(ctx, f'[ Successfully blocked server `{server}`. ]', ephemeral=True)
        
    @block_server.autocomplete('server')
    async def block_server_autocomplete(self, ctx: AutocompleteContext):
        
        server_data = await db.fetch_server_data(ctx.guild_id)
        
        transmitted_servers = server_data.transmittable_servers
        
        server = ctx.input_text
        
        servers = []
        
        for server_id, server_name in transmitted_servers.items():
            
            if not server:
                servers.append({'name': server_name, 'value': server_id})
                continue
            
            if server.lower() in server_name.lower():
                servers.append({'name': server_name, 'value': server_id})
                
        await ctx.send(servers)
    
    available_languages = [
        SlashCommandChoice(
            name='English', value='english'
        ),
        
        SlashCommandChoice(
            name='Russian (Shop Only)', value='russian'
        )
    ]
    
    @server_settings.subcommand(sub_cmd_description='Change the bot\'s language.')
    @slash_default_member_permission(Permissions.MANAGE_GUILD)
    @slash_option(description='DEFAULT: english', name='value', opt_type=OptionType.STRING, required=True, choices=available_languages)
    async def bot_language(self, ctx: SlashContext, value):
        
        await db.update('ServerData', 'language', ctx.guild_id, value)
        
        await ctx.send(f'[ Successfully changed the bot\'s language to `{value}`. ]', ephemeral=True)