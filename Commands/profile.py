from interactions import *
import Utilities.badge_manager as bm
import database as db
from Utilities.fancysend import *
import Utilities.profile_viewer as view
import aiofiles
import json
from datetime import datetime, timedelta
from uuid import uuid4
import os
from interactions.api.events import Component


class Command(Extension):

    async def open_backgrounds(self):
        async with aiofiles.open('Data/backgrounds.json', 'r') as f:
            strdata = await f.read()

        return json.loads(strdata)

    @slash_command(description='All things to do with profiles.')
    async def profile(self, ctx):
        pass

    @profile.subcommand(sub_cmd_description='Give someone a sun!')
    @slash_option(description='Who you want to give it to.', name='user', opt_type=OptionType.USER, required=True)
    async def give_sun(self, ctx: SlashContext, user: User):

        if user.bot:
            await fancy_message(ctx, "[ Can't send bots suns! ]", color=0xFF0000, ephemeral=True)
            return

        if user.id == ctx.author.id:
            await fancy_message(ctx, "[ Can't give yourself a sun! ]", color=0xFF0000, ephemeral=True)
            return

        get_sun_reset_time = await db.get('user_data', ctx.user.id, 'daily_sun_timestamp')

        if get_sun_reset_time is None:
            last_reset_time = datetime(2000, 1, 1, 0, 0, 0)
        else:
            last_reset_time = datetime.strptime(get_sun_reset_time, '%Y-%m-%d %H:%M:%S')

        now = datetime.now()

        if now < last_reset_time:
            time_unix = last_reset_time.timestamp()
            return await fancy_message(ctx, f"[ You've already given a sun to someone! You can give one again <t:{int(time_unix)}:R>. ]", ephemeral=True, color=0xFF0000)

        # reset the limit if it is a new day
        if now >= last_reset_time:
            reset_time = now + timedelta(days=1)
            await db.set('user_data', 'daily_sun_timestamp', ctx.user.id, reset_time.strftime('%Y-%m-%d %H:%M:%S'))

        await bm.increment_value(ctx, 'suns')
        await bm.increment_value(ctx, 'suns', user)

        await ctx.send(f'[ {ctx.author.mention} gave {user.mention} a sun! <:Sun:1026207773559619644> ]')

    @profile.subcommand(sub_cmd_description='Edit your profile.')
    async def edit(self, ctx: SlashContext):

        uid = uuid4()

        edit_buttons = [
            Button(label='Edit Background', custom_id=f'background{uid}', style=ButtonStyle.PRIMARY),
            Button(label='Edit Description', custom_id=f'description{uid}', style=ButtonStyle.PRIMARY),
        ]

        await ctx.send('What do you want to edit?', components=edit_buttons, ephemeral=True)

        while True:
            button: Component = await self.client.wait_for_component(components=edit_buttons)
            
            button_ctx: ComponentContext = button.ctx

            data = button_ctx.custom_id

            if (data == f'description{uid}'):
                modal = Modal(
                    ShortText(
                        label='Edit Profile Description',
                        custom_id='description',
                        placeholder='Enter a description for your profile.'
                    ),
                    title='Edit Profile Description',
                    custom_id='ModalSus'
                )

                await button_ctx.send_modal(modal)

            if (data == f'background{uid}'):

                user_backgrounds = await db.get('user_data', ctx.user.id, 'unlocked_backgrounds')

                backgrounds = await self.open_backgrounds()

                profile_background_choices = []

                for i, bg in enumerate(backgrounds['background']):

                    if i in user_backgrounds:
                        profile_background_choices.append(
                            StringSelectOption(
                                label=bg['name'],
                                value=str(i)
                            )
                        )

                menu = StringSelectMenu(*profile_background_choices, custom_id='selection')

                await button_ctx.send('Select a profile background.', components=menu, ephemeral=True)

                option: Component = await self.client.wait_for_component(components=menu)
                
                SelectOption_: ComponentContext = option.ctx

                id_ = int(ctx.user.id)

                bg_id = SelectOption_.values[0]

                get_bg = backgrounds['background'][int(bg_id)]

                await db.set('user_data', 'equipped_background', ctx.user.id, int(bg_id))

                await button_ctx.send(
                    f'[ Successfully set profile background to: ``{get_bg["name"]}``, use </profile view:8328932897324897> to view your changes. ]',
                    ephemeral=True)

    @profile.subcommand(sub_cmd_description='View a profile.')
    @slash_option(description='The user\'s profile to view.', name='user', opt_type=OptionType.USER, required=True)
    async def view(self, ctx: SlashContext, user: User):

        if user.bot:
            return await ctx.send('[ Cannot view profiles of bots. ]', ephemeral=True)

        msg = f'[ Loading {user.username}\'s profile... <a:loading:1026539890382483576> ]'

        message = await ctx.send(msg)

        await view.DrawBadges(ctx, user)

        img_ = File('Images/Profile Viewer/result.png', description=f'{user.username}\'s profile.')

        await message.edit(content='', files=img_)

        os.remove('Images/Profile Viewer/result.png')

    @modal_callback('ModalSus')
    async def set_description(self, ctx: ModalContext, description: str):
        id_ = int(ctx.user.id)

        await db.set('user_data', 'profile_description', id_, description)

        await ctx.send(
            f'[ Successfully set profile description to: ``{description}``, use </profile view:8328932897324897> to view your changes. ]',
            ephemeral=True)

    choices = [
        SlashCommandChoice(name='Sun Amount', value='suns'),
        SlashCommandChoice(name='Wool Amount', value='wool'),
        SlashCommandChoice(name='Times Shattered', value='times_shattered'),
        SlashCommandChoice(name='Times Asked', value='times_asked'),
        SlashCommandChoice(name='Times Messaged', value='times_messaged'),
        SlashCommandChoice(name='Times Transmitted', value='times_transmitted')
    ]

    @profile.subcommand(sub_cmd_description='View how much times you need to unlock a new badge.')
    @slash_option(description='The badge to view.', name='badge', opt_type=OptionType.STRING, choices=choices, required=True)
    async def next_badge(self, ctx: SlashContext, badge: str):

        amount = await db.get('user_data', ctx.user.id, badge)

        badges = await bm.open_badges()

        amount_required = 0
        get_badge = {}

        for b in badges['Badges']:
            if b['type'] == badge:
                if b['requirement'] < amount:
                    continue
                get_badge = b
                amount_required = b['requirement'] - amount

                break

        description = f'To unlock <:b:{get_badge["emoji"]}> **{get_badge["name"]}** you need to do this action **{amount_required}** more time(s).'

        if badge == "suns" or badge == 'wool':
            description = f'To unlock <:b:{get_badge["emoji"]}> **{get_badge["name"]}** you need to collect **{amount_required}** more {badge}.'

        embed = Embed(
            title='Current Milestone',
            description=description,
            color=0xff171d
        )

        await ctx.send(embeds=embed, ephemeral=True)

    @profile.subcommand(sub_cmd_description="Recover your badges if they've been reset.")
    async def recover_badges(self, ctx: SlashContext):
        wool_amount = await db.get('user_data', ctx.user.id, 'wool')
        sun_amount = await db.get('user_data', ctx.user.id, 'suns')
        times_shattered = await db.get('user_data', ctx.user.id, 'times_shattered')
        times_asked = await db.get('user_data', ctx.user.id, 'times_asked')
        times_transmitted = await db.get('user_data', ctx.user.id, 'times_transmitted')
        times_messaged = await db.get('user_data', ctx.user.id, 'times_messaged')

        get_badges = await bm.open_badges()
        get_badges = get_badges['Badges']

        badges = []

        for i, badge in enumerate(get_badges):
            if badge['type'] == 'wool':
                if badge['requirement'] < wool_amount:
                    badges.append(i)
            if badge['type'] == 'suns':
                if badge['requirement'] < sun_amount:
                    badges.append(i)
            if badge['type'] == 'times_shattered':
                if badge['requirement'] < times_shattered:
                    badges.append(i)
            if badge['type'] == 'times_asked':
                if badge['requirement'] < times_asked:
                    badges.append(i)
            if badge['type'] == 'times_transmitted':
                if badge['requirement'] < times_transmitted:
                    badges.append(i)
            if badge['type'] == 'times_messaged':
                if badge['requirement'] < times_messaged:
                    badges.append(i)

        await db.set('user_data', 'unlocked_badges', ctx.user.id, badges)

        await ctx.send('[ Successfully recovered your badges. ]', ephemeral=True)
