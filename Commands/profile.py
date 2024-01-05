import json
import os
from datetime import datetime, timedelta

import aiofiles
from interactions import *

import Utilities.badge_manager as bm
from Utilities.ItemData import fetch_badge
import Utilities.bot_icons as icons
import Utilities.profile_viewer as profile_viewer
from database import Database as db
from Utilities.fancysend import *
from Utilities.CommandHandler import twm_cmd, twm_subcmd


class Command(Extension):

    async def open_backgrounds(self):
        async with aiofiles.open('Data/backgrounds.json', 'r') as f:
            strdata = await f.read()

        return json.loads(strdata)

    @slash_command(description='All things to do with profiles.')
    async def profile(self, ctx):
        pass

    @slash_command(description='All things to do with Suns.')
    async def sun(self, ctx):
        pass

    @sun.subcommand(sub_cmd_description='Give someone a sun!')
    @slash_option(description='Who you want to give it to.', name='user', opt_type=OptionType.USER, required=True)
    async def give(self, ctx: SlashContext, user: User):

        if user.bot:
            await fancy_message(ctx, "[ Can't send bots suns! ]", color=0xFF0000, ephemeral=True)
            return

        if user.id == ctx.author.id:
            await fancy_message(ctx, "[ Can't give yourself a sun! ]", color=0xFF0000, ephemeral=True)
            return

        get_sun_reset_time = await db.fetch('user_data', 'daily_sun_timestamp', ctx.user.id)

        if get_sun_reset_time is None:
            last_reset_time = datetime(2000, 1, 1, 0, 0, 0)
        else:
            last_reset_time = get_sun_reset_time

        now = datetime.now()

        if now < last_reset_time:
            time_unix = last_reset_time.timestamp()
            return await fancy_message(ctx, f"[ You've already given a sun to someone! You can give one again <t:{int(time_unix)}:R>. ]", ephemeral=True, color=0xFF0000)

        # reset the limit if it is a new day
        if now >= last_reset_time:
            reset_time = now + timedelta(days=1)
            await db.update('user_data', 'daily_sun_timestamp', ctx.user.id, reset_time.strftime('%Y-%m-%d %H:%M:%S'))

        await bm.increment_value(ctx, 'suns')
        await bm.increment_value(ctx, 'suns', user)

        await ctx.send(f'[ {ctx.author.mention} gave {user.mention} a sun! <:Sun:1026207773559619644> ]')

    @sun.subcommand(sub_cmd_description='View who has the most suns!')
    async def leaderboard(self, ctx: SlashContext):
        msg = await ctx.send(
            embeds=Embed(description=f'[ Getting Entries... {icons.loading()} ]', color=0x8b00cc))

        lb: tuple[int, int] = await db.get_leaderboard('suns')

        usernames: str = ''
        value = ''

        msg = await msg.edit(
            embeds=Embed(description=f'[ Fetching Usernames... {icons.loading()} ]', color=0x8b00cc))

        index = 1
        for entry in lb:
            user = await self.bot.fetch_user(entry[0])
            sun = entry[1]
            usernames += f'{index}. **{user.username}** - {icons.sun()} **{sun}**\n'
            index += 1

        embed = Embed(
            title='Sun Leaderboard',
            color=0x8b00cc
        )

        embed.add_field(name='Users', value=usernames, inline=True)
        embed.set_footer(text='Give suns using /sun give <user>!')

        await msg.edit(embeds=embed)
        
    @profile.subcommand(sub_cmd_description='View a profile.')
    @slash_option(description='The user\'s profile to view.', name='user', opt_type=OptionType.USER, required=True)
    async def view(self, ctx: SlashContext, user: User):

        if user.bot:
            return await ctx.send('[ Cannot view profiles of bots. ]', ephemeral=True)

        msg = f'[ Loading {user.username}\'s profile... <a:loading:1026539890382483576> ]'

        message = await fancy_message(ctx, msg)

        await profile_viewer.draw_badges(user)
        
        button = Button(
            style=ButtonStyle.URL,
            url=f'https://www.theworldmachine.xyz/profile',
            label='Edit Profile',
        )

        img_ = File('Images/Profile Viewer/result.png', description=f'{user.username}\'s profile.')

        await message.edit(components=button, content='', embed=[], files=img_)

        os.remove('Images/Profile Viewer/result.png')

    choices = [
        SlashCommandChoice(name='Sun Amount', value='suns'),
        SlashCommandChoice(name='Wool Amount', value='wool'),
        SlashCommandChoice(name='Times Shattered', value='times_shattered'),
        SlashCommandChoice(name='Times Asked', value='times_asked'),
        SlashCommandChoice(name='Times Messaged', value='times_messaged'),
        SlashCommandChoice(name='Times Transmitted', value='times_transmitted')
    ]
