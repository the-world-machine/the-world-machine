import asyncio
import json
import uuid

import aiofiles
import aiohttp
import humanfriendly
from interactions import *
from interactions.api.events import MessageCreate, Component

import database as db
import load_data
from Utilities.badge_manager import increment_value
from Utilities.fancysend import *


class Transmit(Extension):
    transmit_characters = None

    async def load_character(self):
        async with aiofiles.open('Data/transmit_characters.json', 'r') as f:
            strdata = await f.read()

        self.transmit_characters = json.loads(strdata)

    initial_connected_server = None
    next_connected_server = None

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

        if self.initial_connected_server is not None:
            return await fancy_message(ctx, '[ Two servers are already transmitting! ]')

        self.initial_connected_server = {"server_id": 1, "channel_id": 2}
        self.next_connected_server = {"server_id": 1, "channel_id": 2}

        servers = db.fetch('server_data', 'transmittable_servers', ctx.guild.id)
        can_transmit = db.fetch('server_data', 'transmit_channel', ctx.guild.id)

        if can_transmit is None:
            self.initial_connected_server = None
            self.next_connected_server = None

            return await fancy_message(ctx,
                                       '[ This server has opted to disable call transmissions or has simply not set a channel. ]',
                                       ephemeral=True)

        if servers is None:
            self.initial_connected_server = None
            self.next_connected_server = None

            return await fancy_message(ctx,
                                       '[ This server doesn\'t know any other servers! Connect using ``/transmit connect``! ]',
                                       ephemeral=True)

        options = []

        server_name = ''

        for server in servers:
            options.append(
                StringSelectOption(
                    label=server['name'],
                    value=server['id']
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

        get_channel = db.fetch('server_data', 'transmit_channel', other_server)

        if get_channel is None:
            self.initial_connected_server = None
            self.next_connected_server = None

            return await fancy_message(select_results.ctx,
                                       '[ Sorry, but the server you selected has opted to disable call transmissions, or simply has not set a channel. ]',
                                       color=0xfa272d, ephemeral=True)

        other_server_channel = await self.client.fetch_channel(get_channel, force=True)

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
            self.initial_connected_server = None
            self.next_connected_server = None

            await other_server_message.edit(embed=embed_timeout_one, components=[])
            await message.edit(embed=embed_timeout_two)
            return

        await other_server_ctx.ctx.defer(edit_origin=True)

        button_id = other_server_ctx.ctx.custom_id

        if button_id == 'decline_phone':

            self.initial_connected_server = None
            self.next_connected_server = None

            await other_server_message.edit(embed=embed_cancel_one, components=[])
            await message.edit(embed=embed_cancel_two)
        else:

            self.initial_connected_server = {"server_id": int(ctx.guild_id), "channel_id": int(ctx.channel_id),
                                             "users": self.transmit_characters.copy()}
            self.next_connected_server = {"server_id": int(other_server), "channel_id": int(other_server_channel.id),
                                          "users": self.transmit_characters.copy()}

            await  asyncio.gather(
                self.on_connection_first(int(ctx.user.id), message),
                self.on_connection_second(int(other_server_ctx.ctx.user.id), other_server_message)
            )

    @transmit.subcommand(sub_cmd_description='Transmit to another server.')
    async def connect(self, ctx: SlashContext):

        await self.load_character()

        if self.initial_connected_server is None:
            self.initial_connected_server = {"server_id": int(ctx.guild.id), "channel_id": int(ctx.channel_id),
                                             "users": self.transmit_characters.copy()}

            embed = await self.embed_manager('initial_connection')

            cancel = Button(
                style=ButtonStyle.DANGER,
                label='Cancel',
                custom_id='haha cancel go brrr'
            )

            msg = await ctx.send(embeds=embed, components=cancel)

            cancel_timer = 50

            async def check(component: Component):
                if ctx.user.id == component.ctx.user.id:
                    return True
                else:
                    await component.ctx.send(
                        f'[ Only the initiator of this transmission ({ctx.user.mention}) can cancel it! ]',
                        ephemeral=True)
                    return False

            await self.change_status_waiting()

            task = asyncio.create_task(self.client.wait_for_component(components=cancel, check=check))

            while self.next_connected_server is None:
                done, result = await asyncio.wait({task}, timeout=1)

                if not done:
                    cancel_timer -= 1

                    embed.set_footer(
                        text=f'[ This transmission will be automatically cancelled in {cancel_timer} seconds. ]')

                    await msg.edit(embeds=embed, components=cancel)

                    if cancel_timer == 0:
                        self.initial_connected_server = None
                        self.next_connected_server = None

                        embed = await self.on_cancel('timeout', ctx.guild_id, ctx)

                        await msg.edit(embeds=embed, components=[])
                        return

                    continue

                self.initial_connected_server = None
                self.next_connected_server = None

                button_ctx = task.result()

                embed = await self.on_cancel('manual', ctx.guild_id, button_ctx)

                await msg.edit(embeds=embed, components=[])
                return

            await increment_value(ctx, 'times_transmitted', ctx.user)

            await self.on_connection_first(int(ctx.user.id), msg)
            return

        if self.initial_connected_server['server_id'] == int(ctx.guild_id):
            await ctx.send('[ You are already transmitting! ]', ephemeral=True)
            return

        if self.next_connected_server is None:
            self.next_connected_server = {"server_id": int(ctx.guild.id), "channel_id": int(ctx.channel_id),
                                          "users": self.transmit_characters.copy()}

            embed = await self.embed_manager('initial_connection')

            msg = await ctx.send(embeds=embed)

            await increment_value(ctx, 'times_transmitted', ctx.user)

            await self.on_connection_second(int(ctx.user.id), msg)
            return

        if self.next_connected_server['server_id'] == int(ctx.guild_id):
            await ctx.send('[ You are already transmitting! ]', ephemeral=True)
            return

        await ctx.send('[ Two servers are already transmitting! ]', ephemeral=True)
        return

    async def on_connection_first(self, id_, msg: Message):

        get_guild_id = self.initial_connected_server['server_id']

        servers: list = db.fetch('server_data', 'transmittable_servers', get_guild_id)

        if servers is None:
            guild = await self.client.fetch_guild(self.next_connected_server['server_id'])

            db.update('server_data', 'transmittable_servers', get_guild_id,
                      json.dumps([{'name': guild.name, 'id': int(guild.id)}]))
        else:
            for server in servers:
                if server['id'] == self.next_connected_server['server_id']:
                    break

                guild = await self.client.fetch_guild(self.next_connected_server['server_id'])

                servers.append({'name': guild.name, 'id': int(guild.id)})

                db.update('server_data', 'transmittable_servers', get_guild_id, servers)

        btn_id = uuid.uuid4()

        disconnect = Button(
            style=ButtonStyle.DANGER,
            label='Disconnect',
            custom_id=str(btn_id)
        )

        server_name = await self.client.fetch_guild(self.next_connected_server['server_id'])

        async def check(component: Component):
            if id_ == int(component.ctx.user.id):
                return True
            else:
                await component.ctx.send(f'[ Only the initiator of this transmission (<@{id_}>) can cancel it! ]',
                                ephemeral=True)
                return False

        task = asyncio.create_task(self.client.wait_for_component(components=disconnect, check=check))

        disconnect_timer = 600

        embed = await self.embed_manager('connected')
        embed.description = f'[ Currently connected to **{server_name.name}**! ]'

        while self.initial_connected_server is not None:
            done, _ = await asyncio.wait({task}, timeout=1)

            if not done:

                time = humanfriendly.format_timespan(disconnect_timer)

                embed.set_footer(text=f'Transmission will end in {time}.')

                await msg.edit(embeds=embed, components=disconnect)

                disconnect_timer -= 1

                if disconnect_timer == 30:
                    await msg.reply('[ Transmission will end in 30 seconds. ]')

                if disconnect_timer == 0:
                    embed = await self.on_cancel('transmittime', id=get_guild_id)

                    self.initial_connected_server = None
                    self.next_connected_server = None

                    await msg.edit(embeds=embed, components=[])
                    await msg.reply(embeds=embed)
                    return

                continue  # * Important

            if disconnect_timer == 0:
                embed = await self.on_cancel('transmittime', id=get_guild_id)

                self.initial_connected_server = None
                self.next_connected_server = None

                await msg.edit(embeds=embed, components=[])
                await msg.reply(embeds=embed)
                return

            embed = await self.on_cancel('manual', get_guild_id, task.result().ctx)

            await msg.edit(embeds=embed, components=[])
            await msg.reply(embeds=embed)

            self.initial_connected_server = None
            self.next_connected_server = None

            return

        embed = await self.on_cancel('server', id=get_guild_id)

        await msg.edit(embeds=embed, components=[])
        await msg.reply(embeds=embed)

        return

    async def on_connection_second(self, id_, msg: Message):

        await self.change_status_normal()

        get_guild_id = self.next_connected_server['server_id']

        servers: list = db.fetch('server_data', 'transmittable_servers', get_guild_id)

        if servers == None:
            guild = await self.client.fetch_guild(self.initial_connected_server['server_id'])

            db.update('server_data', 'transmittable_servers', get_guild_id,
                      json.dumps([{'name': guild.name, 'id': int(guild.id)}]))
        else:
            for server in servers:
                if server['id'] == self.initial_connected_server['server_id']:
                    break

                guild = await self.client.fetch_guild(self.initial_connected_server['server_id'])

                servers.append({'name': guild.name, 'id': int(guild.id)})

                db.update('server_data', 'transmittable_servers', get_guild_id, servers)

        btn_id = uuid.uuid4()

        disconnect = Button(
            style=ButtonStyle.DANGER,
            label='Disconnect',
            custom_id=str(btn_id)
        )

        server_name = await self.client.fetch_guild(self.initial_connected_server['server_id'])

        async def cancel_check(ctx_: Component):
            if id_ == int(ctx_.ctx.user.id):
                return True
            else:
                await ctx_.ctx.send(f'[ Only the initiator of this transmission (<@{id_}>) can cancel it! ]',
                                    ephemeral=True)
                return False

        task = asyncio.create_task(self.client.wait_for_component(components=disconnect, check=cancel_check))

        disconnect_timer = 600

        embed = await self.embed_manager('connected')
        embed.description = f'[ Currently connected to **{server_name.name}**! ]'

        await msg.edit(embeds=embed, components=disconnect)

        while self.next_connected_server != None:
            done, _ = await asyncio.wait({task}, timeout=1)

            if not done:

                time = humanfriendly.format_timespan(disconnect_timer)

                embed.set_footer(text=f'Transmission will end in {time}.')

                await msg.edit(embeds=embed, components=disconnect)

                disconnect_timer -= 1

                if disconnect_timer == 30:
                    await msg.reply('[ Transmission will end in 30 seconds. ]')

                if disconnect_timer == 0:
                    embed = await self.on_cancel('transmittime', id=get_guild_id)

                    self.initial_connected_server = None
                    self.next_connected_server = None

                    await msg.edit(embeds=embed, components=[])
                    await msg.reply(embeds=embed)
                    return

                continue  # * Important

            if disconnect_timer == 0:
                embed = await self.on_cancel('transmittime', id=get_guild_id)

                self.initial_connected_server = None
                self.next_connected_server = None

                await msg.edit(embeds=embed, components=[])
                await msg.reply(embeds=embed)
                return

            embed = await self.on_cancel('manual', id=get_guild_id)

            await msg.edit(embeds=embed, components=[])
            await msg.reply(embeds=embed)

            self.initial_connected_server = None
            self.next_connected_server = None

            return

        embed = await self.on_cancel('server', id=get_guild_id)

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

    def check_anonymous(self, guild_id: int, d_user: User):

        anonymous = db.fetch('server_data', 'transmit_anonymous', guild_id)

        if guild_id == self.initial_connected_server['server_id']:
            characters = self.initial_connected_server['users']
        else:
            characters = self.next_connected_server['users']

        user: Transmit.TransmitUser

        if anonymous:

            for i, character in enumerate(characters):
                if character['id'] is None or character['id'] == d_user.id:
                    user = Transmit.TransmitUser(character['name'], d_user.id, character['image'])

                    characters[i]['id'] = d_user.id

                    if guild_id == self.initial_connected_server['server_id']:
                        self.initial_connected_server['users'] = characters
                    else:
                        self.next_connected_server['users'] = characters

                    return user

            user = Transmit.TransmitUser(self.transmit_characters[0]['name'], d_user.id,
                                         self.transmit_characters[0]['image'])

            if guild_id == self.initial_connected_server['server_id']:
                self.initial_connected_server['users'] = characters
            else:
                self.next_connected_server['users'] = characters
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

        if self.next_connected_server is not None:

            user = self.check_anonymous(guild.id, message.author)

            first_server = self.initial_connected_server
            second_server = self.next_connected_server

            can_pass = False
            other_connection = None
            allow_images = True

            if first_server['channel_id'] == channel.id:
                can_pass = True
                other_connection = await self.client.fetch_channel(second_server['channel_id'])
                allow_images = db.fetch('server_data', 'transmit_images', second_server['server_id'])

            if second_server['channel_id'] == channel.id:
                can_pass = True
                other_connection = await self.client.fetch_channel(first_server['channel_id'])
                allow_images = db.fetch('server_data', 'transmit_images', first_server['server_id'])

            if can_pass:
                embed = await self.message_manager(message, user, allow_images)

                async with other_connection.typing:
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

    async def DownloadImage(self, image_url, filename):
        async with aiohttp.ClientSession() as session:
            async with session.get(image_url) as resp:
                if resp.status == 200:
                    f = await aiofiles.open(f'Images/{filename}', mode='wb')
                    await f.write(await resp.read())
                    await f.close()

        return File(f'Badges/Images/{filename}.png')

    async def on_cancel(self, cancel_reason, id: int, button_ctx=None):

        db.update('server_data', 'transmit_characters', id, json.dumps(self.transmit_characters))

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
