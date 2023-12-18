import asyncio
import json
import uuid
from typing import Union

import aiofiles
import aiohttp
import humanfriendly
from interactions import *
from interactions.api.events import MessageCreate, Component

from database import Database as db
import load_data
from Utilities.badge_manager import increment_value
from Utilities.fancysend import *

from Utilities.TransmissionConnectionManager import *


class Transmit(Extension):
    transmit_characters = None
    async def load_character(self):
        async with aiofiles.open('Data/transmit_characters.json', 'r') as f:
            strdata = await f.read()

        self.transmit_characters = json.loads(strdata)

    async def change_status_waiting(self):
        await self.client.change_presence(status=Status.IDLE,
                                          activity=Activity(name="Transmission 📺", type=ActivityType.WATCHING))

    async def change_status_normal(self):
        await self.client.change_presence(status=Status.ONLINE,
                                          activity=Activity(name=load_data.load_config('MOTD'), type=ActivityType.PLAYING))

    @slash_command(description='Transmit to over servers!')
    async def transmit(self, ctx: SlashContext):
        pass

    @transmit.subcommand(sub_cmd_description='Connect to a server you already know.')
    async def call(self, ctx: SlashContext):

        await self.load_character()

        server_ids: dict = await db.fetch('server_data', 'transmittable_servers', ctx.guild.id)
        can_transmit = await db.fetch('server_data', 'transmit_channel', ctx.guild.id)

        if can_transmit is None:

            return await fancy_message(ctx,
                                       '[ This server has opted to disable call transmissions or has simply not set a channel. ]',
                                       ephemeral=True)

        if server_ids is None:

            return await fancy_message(ctx,
                                       '[ This server doesn\'t know any other servers! Connect using ``/transmit connect``! ]',
                                       ephemeral=True)

        options = []

        server_name = ''

        for server in server_ids.keys():
            options.append(
                StringSelectOption(
                    label=server_ids[server],
                    value=server
                )
            )

        server_list = StringSelectMenu(
            options,
            custom_id=str(ctx.guild.id),
            placeholder='Connect to...',
        )

        await ctx.send(components=server_list, ephemeral=True)

        select_results = await self.client.wait_for_component(components=server_list)

        other_server = int(select_results.ctx.values[0])

        get_channel = await db.fetch('server_data', 'transmit_channel', other_server)

        if get_channel is None:

            return await fancy_message(select_results.ctx,
                                       '[ Sorry, but the server you selected has opted to disable call transmissions, or simply has not set a channel. ]',
                                       color=0xfa272d, ephemeral=True)

        other_server_channel: GuildText = await self.client.fetch_channel(get_channel, force=True)

        server_name = other_server_channel.guild.name

        connect_button = Button(
            style=ButtonStyle.PRIMARY,
            label='Answer',
            custom_id='answer_phone'
        )

        disconnect_button = Button(
            style=ButtonStyle.DANGER,
            label='Decline',
            custom_id='decline_phone'
        )

        embed_one = await fancy_embed(f'[ Calling **{server_name}**... <a:loading:1026539890382483576> ]')

        embed_timeout_one = await fancy_embed('``[ Sorry! You took too long to respond! ]``', color=0xfa272d)
        embed_timeout_two = await fancy_embed('``[ Sorry! The other server took too long to respond! ]``', color=0xfa272d)

        embed_cancel_one = await fancy_embed('``[ Successfully Declined. ]``', color=0xfa272d)
        embed_cancel_two = await fancy_embed('``[ Sorry! The other server declined the call! ]``', color=0xfa272d)

        message = await select_results.ctx.send(embed=embed_one)

        other_server_message = await fancy_message(other_server_channel, f'[ **{ctx.guild.name}** is calling you! ]', components=[connect_button, disconnect_button])

        try:
            other_server_ctx = await self.client.wait_for_component(components=[connect_button, disconnect_button], timeout=60)
        except:

            await other_server_message.edit(embed=embed_timeout_one, components=[])
            await message.edit(embed=embed_timeout_two)
            return

        await other_server_ctx.ctx.defer(edit_origin=True)

        button_id = other_server_ctx.ctx.custom_id

        if button_id == 'decline_phone':

            await other_server_message.edit(embed=embed_cancel_one, components=[])
            await message.edit(embed=embed_cancel_two)
        else:

            create_connection(ctx.guild_id, ctx.channel_id)
            connect_to_transmission(other_server, other_server_channel.id)

            await  asyncio.gather(
                self.on_transmission(ctx.author.user, message, ctx.guild_id),
                self.on_transmission(other_server_ctx.ctx.user, other_server_message, other_server)
            )

    @transmit.subcommand(sub_cmd_description='Transmit to another server.')
    async def connect(self, ctx: SlashContext):

        await self.load_character()

        if len(transmissions) == 0:
            create_connection(ctx.guild_id, ctx.channel_id)

            embed = await self.embed_manager('initial_connection')

            cancel = Button(
                style=ButtonStyle.DANGER,
                label='Cancel',
                custom_id='haha cancel go brrr'
            )

            msg = await ctx.send(embeds=embed, components=cancel)

            cancel_timer = 50

            async def check_(component: Component):
                if ctx.user.id == component.ctx.user.id:
                    return True
                else:
                    await component.ctx.send(
                        f'[ Only the initiator of this transmission ({ctx.user.mention}) can cancel it! ]',
                        ephemeral=True)
                    return False

            await self.change_status_waiting()

            task = asyncio.create_task(self.client.wait_for_component(components=cancel, check=check_))

            while not connection_alive(ctx.guild_id):
                done, result = await asyncio.wait({task}, timeout=1)

                if not done:
                    cancel_timer -= 1

                    embed.set_footer(
                        text=f'[ This transmission will be automatically cancelled in {cancel_timer} seconds. ]')

                    await msg.edit(embeds=embed, components=cancel)

                    if cancel_timer == 0:
                        remove_connection(ctx.guild_id)

                        embed = await self.on_cancel('timeout', ctx.guild_id, ctx)

                        await msg.edit(embeds=embed, components=[])
                        return

                    continue

                remove_connection(ctx.guild_id)

                button_ctx = task.result()

                embed = await self.on_cancel('manual', ctx.guild_id, button_ctx)

                await msg.edit(embeds=embed, components=[])
                return

            await increment_value(ctx, 'times_transmitted', ctx.user)

            await self.on_transmission(ctx.user, msg, ctx.guild_id)
            return

        connected = check_if_connected(ctx.guild_id)

        if connected:
            await ctx.send('[ You are already transmitting! ]', ephemeral=True)
            return
        else:
            embed = await self.embed_manager('initial_connection')

            msg = await ctx.send(embeds=embed)

            await increment_value(ctx, 'times_transmitted', ctx.user)

            connect_to_transmission(ctx.guild_id, ctx.channel_id)
            await self.on_transmission(ctx.user, msg, ctx.guild_id)
            return

    async def on_transmission(self, user: User, msg: Message, server_id: int):

        transmission = get_transmission(server_id)

        this_server: Guild
        other_server: Guild

        if server_id == transmission.connection_a.server_id:
            this_server = await self.client.fetch_guild(transmission.connection_a.server_id)
            other_server = await self.client.fetch_guild(transmission.connection_b.server_id)
        else:
            this_server = await self.client.fetch_guild(transmission.connection_b.server_id)
            other_server = await self.client.fetch_guild(transmission.connection_a.server_id)

        servers = await db.fetch('server_data', 'transmittable_servers', server_id)

        servers[str(other_server.id)] = other_server.name

        await db.update('server_data', 'transmittable_servers', server_id, servers)

        btn_id = uuid.uuid4()

        disconnect = Button(
            style=ButtonStyle.DANGER,
            label='Disconnect',
            custom_id=str(btn_id)
        )

        async def check_button(component: Component):
            if user.id == component.ctx.user.id:
                return True
            else:
                await component.ctx.send(f'[ Only the initiator of this transmission ({User.mention}) can cancel it! ]',
                                ephemeral=True)
                return False

        task = asyncio.create_task(self.client.wait_for_component(components=disconnect, check=check_button))

        disconnect_timer = 600

        embed = await self.embed_manager('connected')
        embed.description = f'[ Currently connected to **{other_server.name}**! ]'

        while connection_alive(server_id):
            done, _ = await asyncio.wait({task}, timeout=1)

            if not done:

                if disconnect_timer % 10 == 0:
                    time = humanfriendly.format_timespan(disconnect_timer)

                    embed.set_footer(text=f'Transmission will end in {time}.')

                    await msg.edit(embeds=embed, components=disconnect)

                disconnect_timer -= 1

                if disconnect_timer == 30:
                    await msg.reply('[ Transmission will end in 30 seconds. ]')

                if disconnect_timer == 0:
                    embed = await self.on_cancel('transmittime', id=server_id)

                    remove_connection(server_id)

                    await msg.edit(embeds=embed, components=[])
                    await msg.reply(embeds=embed)
                    return

                continue  # * Important

            embed = await self.on_cancel('manual', server_id, task.result().ctx)

            await msg.edit(embeds=embed, components=[])
            await msg.reply(embeds=embed)

            remove_connection(server_id)

            return

        embed = await self.on_cancel('server', id=server_id)
        
        remove_connection(server_id)

        await msg.edit(embeds=embed, components=[])
        await msg.reply(embeds=embed)

        return

    class TransmitUser:
        name: str
        id: int
        image: str

        def __init__(self, name, u_id, image):
            self.name = name
            self.id = u_id
            self.image = image

    async def check_anonymous(self, guild_id: int, d_user: User):

        anonymous = await db.fetch('server_data', 'transmit_anonymous', guild_id)
        characters = await db.fetch('server_data', 'transmit_characters', guild_id)

        user: Transmit.TransmitUser

        if anonymous:

            for i, character in enumerate(characters):
                if character['id'] is None or character['id'] == d_user.id:
                    user = Transmit.TransmitUser(character['name'], d_user.id, character['image'])

                    characters[i]['id'] = d_user.id

                    await db.update('server_data', 'transmit_characters', guild_id, characters)

                    return user

            user = Transmit.TransmitUser(self.transmit_characters[0]['name'], d_user.id,
                                         self.transmit_characters[0]['image'])
        else:
            user = Transmit.TransmitUser(d_user.username, d_user.id, d_user.display_avatar.url)

        return user

    @listen()
    async def on_message_create(self, event: MessageCreate):

        message = event.message
        channel = message.channel
        guild = message.guild

        if channel.type == ChannelType.DM:
            return

        if message.author.id == 1015629604536463421 or message.author.id == 1028058097383641118:
            return

        if connection_alive(guild.id):
            
            if message.author.id == self.client.user.id:
                return

            user = await self.check_anonymous(guild.id, message.author)
            transmission = get_transmission(guild.id)

            first_server = transmission.connection_a
            second_server = transmission.connection_b

            can_pass = False
            other_connection = None
            allow_images = True

            if first_server.channel_id == channel.id:
                can_pass = True
                other_connection = await self.client.fetch_channel(second_server.channel_id)
                allow_images = await db.fetch('server_data', 'transmit_images', second_server.server_id)

            if second_server.channel_id == channel.id:
                can_pass = True
                other_connection = await self.client.fetch_channel(first_server.channel_id)
                allow_images = await db.fetch('server_data', 'transmit_images', first_server.server_id)

            if can_pass:
                embed = await self.message_manager(message, user, allow_images)

                await other_connection.send(embeds=embed)

    async def message_manager(self, message: Message, user: TransmitUser, allow_images: bool):

        final_text = message.content

        embed = Embed(
            color=0x2b2d31,
            description=final_text
        )

        if len(message.attachments) > 0:
            image = message.attachments[0].url

            if '.mp4' in image or '.mov' in image:
                embed.video = EmbedAttachment(url=image)
                embed.set_footer('User sent a video, but discord does not allow bots to send videos in embeds.')
            elif allow_images:
                embed.image = EmbedAttachment(url=image)
            else:
                final_text += '\n\n[IMAGE]'

        embed.set_author(name=user.name, icon_url=user.image)

        embed.description = final_text

        return embed
                    
                    
    async def on_cancel(self, cancel_reason, id: int, button_ctx=None):

        await db.update('server_data', 'transmit_characters', id, json.dumps(self.transmit_characters))

        await self.change_status_normal()

        if cancel_reason == 'timeout':
            return Embed(
                title='Transmission Cancelled.',
                description='Looks like no one wants to talk...',
                color=0xff1a1a
            )

        if cancel_reason == 'manual':
            return Embed(
                title='Transmission Cancelled.',
                description=f'{button_ctx.author.mention} cancelled the transmission.',
                color=0xff1a1a
            )

        if cancel_reason == 'server':
            return Embed(
                title='Transmission Cancelled.',
                description='The other server cancelled the transmission.',
                color=0xff1a1a
            )

        if cancel_reason == 'transmittime':
            return Embed(
                title='Transmission Ended.',
                description='You ran out of transmission time.',
                color=0xff1a1a
            )

    async def embed_manager(self, embed_type: str):
        if embed_type == 'initial_connection':
            return Embed(
                title='Transmission Starting!',
                description='Waiting for a connection... <a:loading:1026539890382483576>',
                color=0x933397
            )

        if embed_type == 'connected':
            return Embed(
                title='Connected!',
                color=0x47ff1a
            )


def setup(client):
    Transmit(client)
