from dataclasses import dataclass
import json
import random
from datetime import datetime
import re
import time
from typing import Union

from dateutil import relativedelta
from interactions import *
from interactions.api.events import Component

import utilities.fetch_capsule_characters as chars
from localization.loc import Localization
from utilities.shop.fetch_items import fetch_treasure
from database import UserData, NikogotchiData
from utilities.bot_icons import icon_loading
from utilities.fancy_send import *


@dataclass
class Nikogotchi:
    
    original_name: str
    
    name: str
    immortal: bool
    rarity: int
    status: int
    emoji: str
    health: float
    hunger: float
    attention: float
    cleanliness: float

class Command(Extension):

    async def get_nikogotchi(self, uid: int):
        nikogotchi_data: NikogotchiData = await NikogotchiData(uid).fetch()

        if not nikogotchi_data.data:
            return None

        return Nikogotchi(**nikogotchi_data.data)

    async def save_nikogotchi(self, nikogotchi: Nikogotchi, uid: int):
        
        nikogotchi_data: NikogotchiData = await NikogotchiData(uid).fetch()
        
        data = nikogotchi.__dict__

        await nikogotchi_data.update(data=data)
        
    async def delete_nikogotchi(self, uid: int):
        
        nikogotchi_data = await NikogotchiData(uid).fetch()
        
        await nikogotchi_data.update(data={})

    def nikogotchi_buttons(self, owner_id: int, locale: str):
        prefix = 'action_'
        suffix = f'_{owner_id}'
        
        loc = Localization(locale)

        return [
            Button(
                style=ButtonStyle.SUCCESS,
                label=loc.l('nikogotchi.components.pet'),
                custom_id=f'{prefix}pet{suffix}'
            ),
            Button(
                style=ButtonStyle.SUCCESS,
                label=loc.l('nikogotchi.components.clean'),
                custom_id=f'{prefix}clean{suffix}'
            ),
            Button(
                style=ButtonStyle.PRIMARY,
                label=loc.l('nikogotchi.components.find_treasure'),
                custom_id=f'{prefix}findtreasure{suffix}'
            ),
            Button(
                style=ButtonStyle.GREY,
                emoji=PartialEmoji(id=1147696088250335303),
                custom_id=f'{prefix}refresh{suffix}'
            ),
            Button(
                style=ButtonStyle.DANGER,
                label='X',
                custom_id=f'{prefix}exit{suffix}'
            )
        ]

    async def get_nikogotchi_age(self, uid: int):
        nikogotchi_data: NikogotchiData = await NikogotchiData(uid).fetch()

        return relativedelta.relativedelta(datetime.now(), nikogotchi_data.hatched)

    async def get_main_nikogotchi_embed(self, locale: str, age: relativedelta.relativedelta, dialogue: str,
                                        found_treasure: list[dict], n: Nikogotchi):
        progress_bar = {
            'empty': {
                'start': '<:thebeginningofthesong:1117957176724557824>',
                'middle': '<:themiddleofthesong:1117957179463438387>',
                'end': '<:theendofthesong:1117957159938961598>'
            },
            'filled': {
                'start': '<:thebeginningofthesong:1117957177987051530>',
                'middle': '<:themiddleofthesong:1117957181220864120>',
                'end': '<:theendofthesong:1117957174015041679>'
            }
        }
        
        loc = Localization(locale)

        progress_bar_length = 5

        health_value = round((n.health / 50) * progress_bar_length)
        hunger_value = round((n.hunger / 50) * progress_bar_length)
        attention_value = round((n.attention / 50) * progress_bar_length)
        cleanliness_value = round((n.cleanliness / 50) * progress_bar_length)

        health_progress_bar = ''
        hunger_progress_bar = ''
        attention_progress_bar = ''
        cleanliness_progress_bar = ''

        values = [health_value, hunger_value, attention_value, cleanliness_value]

        for index, value in enumerate(values):
            progress_bar_l = []
            for i in range(progress_bar_length):
                bar_section = 'middle'
                if i == 0:
                    bar_section = 'start'
                elif i == progress_bar_length - 1:
                    bar_section = 'end'

                if i < value:
                    bar_fill = progress_bar['filled'][bar_section]
                else:
                    bar_fill = progress_bar['empty'][bar_section]

                progress_bar_l.append(bar_fill)

            progress = ''.join(progress_bar_l)

            if index == 0:
                health_progress_bar = progress
            elif index == 1:
                hunger_progress_bar = progress
            elif index == 2:
                attention_progress_bar = progress
            elif index == 3:
                cleanliness_progress_bar = progress

        embed = Embed(
            title=n.name,
            color=0x8b00cc
        )

        nikogotchi_status = loc.l('nikogotchi.status.normal')

        if n.attention < 20:
            nikogotchi_status = loc.l('nikogotchi.status.pet', name=n.name)

        if n.cleanliness < 20:
            nikogotchi_status = loc.l('nikogotchi.status.dirty', name=n.name)

        if n.hunger < 20:
            nikogotchi_status = loc.l('nikogotchi.status.hungry', name=n.name)

        if n.status == 3:
            nikogotchi_status = loc.l('nikogotchi.status.treasure', name=n.name)

        treasure_found = ''

        if len(found_treasure) > 0:

            treasures = ''
            looked_over_treasures = []

            for treasure in found_treasure:

                if treasure in looked_over_treasures:
                    continue
                
                amount = found_treasure.count(treasure)

                treasures += f'<:any:{treasure["image"]}> {treasure["name"]} - **x{amount}**\n'
                
                looked_over_treasures.append(treasure)

            treasure_found = loc.l('nikogotchi.status.treasures_found', name=n.name, treasures=treasures)

        if n.health < 20:
            nikogotchi_status = loc.l('nikogotchi.status.danger', name=n.name)

        embed.set_author(name=nikogotchi_status)

        age = loc.l('nikogotchi.status.age', years=age.days, months=age.months, days=age.days)
        
        description = f'''
        {treasure_found}\n
        ❤️  {health_progress_bar} ({int(n.health)} / 50)\n\n🍴  {hunger_progress_bar} ({n.hunger} / 50)\n🫂  {attention_progress_bar} ({n.attention} / 50)\n🧽  {cleanliness_progress_bar} ({n.cleanliness} / 50)\n\n⏰  {age}
        '''

        embed.description = description

        embed.set_image(url=f'https://cdn.discordapp.com/emojis/{n.emoji}.png')
        embed.set_footer(text=dialogue)

        return embed

    @slash_command(description="All things about your Nikogotchi!")
    async def nikogotchi(self, ctx: SlashContext):
        pass

    @nikogotchi.subcommand(sub_cmd_description="Check out your Nikogotchi!")
    async def check(self, ctx: SlashContext):

        uid = ctx.author.id

        nikogotchi_data: NikogotchiData = await NikogotchiData(uid).fetch()
        
        loc = Localization(ctx.locale)

        if nikogotchi_data.data:
            msg = await fancy_message(ctx, loc.l('nikogotchi.loading'))

        else:

            if not nikogotchi_data.nikogotchi_available:
                return await fancy_message(ctx, loc.l('nikogotchi.invalid'), ephemeral=True, color=0xff0000)
            
            viable_nikogotchi = []

            nikogotchi_list = chars.get_characters()

            for character in nikogotchi_list:
                if nikogotchi_data.rarity == character.rarity.value:
                    viable_nikogotchi.append(character)

            selected_nikogotchi: chars.Nikogotchi = random.choice(viable_nikogotchi)

            await nikogotchi_data.update(
                data = {
                    'original_name': selected_nikogotchi.name,
                    'name': selected_nikogotchi.name,
                    'emoji': str(selected_nikogotchi.emoji),
                    'rarity': selected_nikogotchi.rarity.value,
                    'status': 2,
                    'immortal': False,
                    'health': 50,
                    'hunger': 50,
                    'attention': 50,
                    'cleanliness': 50
                },
            
                last_interacted = datetime.now(),
                hatched = datetime.now(),
                nikogotchi_available = False
            )

            nikogotchi = await self.get_nikogotchi(ctx.author.id)

            hatched_embed = Embed(
                title=loc.l('nikogotchi.found.title', name=nikogotchi.name),
                color=0x8b00cc,
                description=loc.l('nikogotchi.found.name')
            )

            hatched_embed.set_image(url=f'https://cdn.discordapp.com/emojis/{nikogotchi.emoji}.png')

            buttons = [
                Button(style=ButtonStyle.GREEN, label=loc.l('general.buttons._yes'), custom_id=f'yes {ctx.author.id}'),
                Button(style=ButtonStyle.RED, label=loc.l('general.buttons._no'), custom_id=f'no {ctx.author.id}')
            ]

            await ctx.send(embed=hatched_embed, components=buttons, ephemeral=True)

            button: Component = await self.bot.wait_for_component(components=buttons)
            button_ctx = button.ctx

            custom_id = button_ctx.custom_id

            if custom_id == f'yes {ctx.author.id}':
                modal = Modal(
                    ShortText(
                        custom_id='name',
                        value=nikogotchi.name,
                        label=loc.l('nikogotchi.found.m_label')
                    ),
                    custom_id='name',
                    title=loc.l('nikogotchi.found.m_title'),
                )

                await button_ctx.send_modal(modal)

                modal_ctx: ModalContext = await self.bot.wait_for_modal(modal)

                await modal_ctx.defer(edit_origin=True)

                nikogotchi.name = modal_ctx.kwargs['name']
            else:
                await button_ctx.defer(edit_origin=True)

            await self.save_nikogotchi(nikogotchi, ctx.author.id)

        await self.nikogotchi_interaction(ctx)

    r_nikogotchi_interaction = re.compile(r'action_(feed|pet|clean|findtreasure|refresh|callback|exit)_(\d+)$')
    @component_callback(r_nikogotchi_interaction)
    async def nikogotchi_interaction(self, ctx: ComponentContext):
        
        try:
            await ctx.defer(edit_origin=True)
            
            match = self.r_nikogotchi_interaction.match(ctx.custom_id)
        
            if not match:
                return
            
            custom_id = match.group(1)
            uid = int(match.group(2))
            
            if ctx.author.id != uid:
                return
        except:
            uid = ctx.author.id
            custom_id = 'refresh'
            
        if custom_id == 'exit':
            await ctx.delete()
            
        loc = Localization(ctx.locale)
            
        nikogotchi_data: NikogotchiData = await NikogotchiData(uid).fetch()
        nikogotchi = await self.get_nikogotchi(uid)
        
        last_interacted = nikogotchi_data.last_interacted

        # Get the current datetime
        current_time = datetime.now()

        # Calculate the time difference in hours
        time_difference = (current_time - last_interacted).total_seconds() / 3600
        
        age = await self.get_nikogotchi_age(int(ctx.author.id))

        await nikogotchi_data.update(last_interacted=current_time)

        modifier = 1

        if nikogotchi.status == 3:
            modifier = 2.5
            
        random_stat_modifier = random.uniform(1, 1.50)

        nikogotchi.hunger = round(max(0, nikogotchi.hunger - time_difference * random_stat_modifier * modifier))
        
        random_stat_modifier = random.uniform(1, 1.50)
        
        nikogotchi.attention = round(max(0, nikogotchi.attention - time_difference * random_stat_modifier * modifier))
        
        random_stat_modifier = random.uniform(1, 1.50)
        
        nikogotchi.cleanliness = round(max(0, nikogotchi.cleanliness - time_difference * random_stat_modifier * modifier))

        if nikogotchi.immortal:
            nikogotchi.hunger = 9999
            nikogotchi.attention = 9999
            nikogotchi.cleanliness = 9999

        if nikogotchi.hunger <= 0 or nikogotchi.attention <= 0 or nikogotchi.cleanliness <= 0:
            nikogotchi.health = round(nikogotchi.health - time_difference * 0.5)

        if nikogotchi.health <= 0:
            embed = Embed(
                title=loc.l('nikogotchi.died_title', name=nikogotchi.name),
                color=0x696969,
                description=loc.l('nikogotchi.died', name=nikogotchi.name, years=age.years, months=age.months, days=age.days, time_difference=time_difference)
            )
            
            await self.delete_nikogotchi(uid)
            
            try:
                await ctx.edit_origin(embed=embed, components=[])
            except:
                await ctx.edit(embed=embed, components=[])
        
        if nikogotchi is None:
            return await ctx.edit_origin(
            embed=Embed(
                title=loc.l('nikogotchi.error_title'),
                description=loc.l('nikogotchi.error_desc')
            ),
            
            components=[
                Button(
                    emoji=PartialEmoji(id=1147696088250335303),
                    custom_id=f'action_refresh_{ctx.author.id}',
                    style=ButtonStyle.GREY)
            ]
        )

        if not custom_id == 'refresh':
            pass

        dialogue = '...'
        
        buttons = self.nikogotchi_buttons(uid, ctx.locale)
        select = await self.feed_nikogotchi(ctx)

        if nikogotchi.status == 2:
            if custom_id == 'pet':
                # Adjust hunger, attention, and cleanliness
                attention_increase = 20
                nikogotchi.attention = min(50, nikogotchi.attention + attention_increase)

                dialogue = random.choice(loc.l(f'nikogotchi.dialogue.{nikogotchi.original_name}.pet'))

            if custom_id == 'clean':
                cleanliness_increase = 30
                nikogotchi.cleanliness = min(50, nikogotchi.cleanliness + cleanliness_increase)

                dialogue = random.choice(loc.l(f'nikogotchi.dialogue.{nikogotchi.original_name}.cleaned'))

            if custom_id == 'findtreasure':
                dialogue = loc.l('nikogotchi.finding_treasure')
                nikogotchi.status = 3

        if custom_id == 'callback':
            nikogotchi.status = 2

        embed = await self.get_main_nikogotchi_embed(ctx.locale, age, dialogue, [], nikogotchi)

        if not custom_id == 'feed':
            if nikogotchi.status == 2:
                buttons[0].disabled = False
                buttons[1].disabled = False
                buttons[2].disabled = False

                buttons[2].label = str(loc.l('nikogotchi.components.find_treasure'))
                buttons[2].custom_id = f'action_findtreasure_{uid}'
            else:
                select.disabled = True
                buttons[0].disabled = True
                buttons[1].disabled = True
                buttons[2].disabled = False

                buttons[2].label = str(loc.l('nikogotchi.components.call_back'))
                buttons[2].custom_id = f'action_callback_{uid}'

        embed.set_image(url=f'https://cdn.discordapp.com/emojis/{nikogotchi.emoji}.png')

        if nikogotchi.status == 3:
            
            user_data: UserData = await UserData(uid).fetch()
            treasures = await fetch_treasure()

            treasures_found = []

            for _ in range(round(time_difference)):
                value = random.randint(0, 5000)
                treasure = ''
                if value > 0:
                    treasure = random.choice(["journal", "bottle", "shirt"])
                if value > 4500:
                    treasure = random.choice(["amber", "pen", "card"])
                if value > 4900:
                    treasure = random.choice(["die", "sun", "clover"])

                treasure_loc: dict = loc.l(f'items.treasures.{treasure}')
                
                treasures_found.append({'name': treasure_loc['name'], 'image': treasures[treasure]['image']})

                user_treasures: dict[str, int] = user_data.owned_treasures
                
                user_treasures[treasure] = user_treasures.get(treasure, 0) + 1
                await user_data.update(owned_treasures=user_treasures)

            select.disabled = True
            buttons[0].disabled = True
            buttons[1].disabled = True
            buttons[2].disabled = False

            buttons[2].label = 'Call Back'
            buttons[2].custom_id = f'action_callback_{uid}'
            
            embed = await self.get_main_nikogotchi_embed(ctx.locale, age, dialogue, treasures_found, nikogotchi)
            embed.set_image(url='')

        await self.save_nikogotchi(nikogotchi, ctx.author.id)
        
        try:
            await ctx.edit_origin(embed=embed, components=[ActionRow(select), ActionRow(*buttons)])
        except:
            await ctx.edit(embed=embed, components=[ActionRow(select), ActionRow(*buttons)])

    async def feed_nikogotchi(self, ctx):
        food_options = []

        nikogotchi_data: NikogotchiData = await NikogotchiData(ctx.author.id).fetch()
        
        nikogotchi = await self.get_nikogotchi(ctx.author.id)
        
        loc = Localization(ctx.locale)
        
        options = False

        if nikogotchi_data.glitched_pancakes > 0:
            food_options.append(
                StringSelectOption(
                    label=loc.l('nikogotchi.components.feed.glitched_pancakes', amount=nikogotchi_data.glitched_pancakes),
                    emoji=PartialEmoji(1152356972423819436),
                    value=f'pancakeglitched_{ctx.author.id}'
                )
            )
            
            options = True

        if nikogotchi_data.golden_pancakes > 0:
            food_options.append(
                StringSelectOption(
                    label=loc.l('nikogotchi.components.feed.golden_pancakes', amount=nikogotchi_data.golden_pancakes),
                    emoji=PartialEmoji(1152330988022681821),
                    value=f'goldenpancake_{ctx.author.id}'
                )
            )
            
            options = True

        if nikogotchi_data.pancakes > 0:
            food_options.append(
                StringSelectOption(
                    label=loc.l('nikogotchi.components.feed.pancakes', amount=nikogotchi_data.pancakes),
                    emoji=PartialEmoji(1147281411854839829),
                    value=f'pancake_{ctx.author.id}'
                )
            )
            
            options = True
            
        placeholder = loc.l('nikogotchi.components.feed.placeholder', name=nikogotchi.name)
        cannot_feed = False
            
        if not options:
            food_options.append(
                StringSelectOption(
                    label=f'no food',
                    value='nofood'
                )
            )
            
            placeholder = loc.l('nikogotchi.components.feed.no_food')
            cannot_feed = True
            
        select = StringSelectMenu(
            *food_options,
            custom_id='feed_food',
            placeholder=placeholder,
            disabled=cannot_feed
        )

        return select

    @component_callback('feed_food')
    async def feed_food(self, ctx: ComponentContext):

        await ctx.defer(edit_origin=True)

        nikogotchi = await self.get_nikogotchi(ctx.author.id)
        data = ctx.values[0].split('_')
        
        value = data[0]
        uid = int(data[1])
        
        if ctx.author.id != uid:
            return

        nikogotchi_data: NikogotchiData = await NikogotchiData(uid).fetch()
        
        pancakes = nikogotchi_data.pancakes
        golden_pancakes = nikogotchi_data.golden_pancakes
        glitched_pancakes = nikogotchi_data.glitched_pancakes

        hunger_increase = 0
        health_increase = 0
        
        loc = Localization(ctx.locale)

        if value == 'goldenpancake':
            if golden_pancakes <= 0:
                dialogue = loc.l('nikogotchi.components.feed.invalid')
            else:
                hunger_increase = 50
                health_increase = 25

                golden_pancakes -= 1
                dialogue = random.choice(loc.l(f'nikogotchi.dialogue.{nikogotchi.original_name}.fed'))
        elif value == 'pancakeglitched':
            if glitched_pancakes <= 0:
                dialogue = loc.l('nikogotchi.components.feed.invalid')
            else:
                hunger_increase = 9999
                health_increase = 9999
                
                glitched_pancakes -= 1
                nikogotchi.immortal = True
                dialogue = loc.l('nikogotchi.components.feed.immortal')
        else:
            if pancakes <= 0:
                dialogue = loc.l('nikogotchi.components.feed.invalid')
            else:
                hunger_increase = 25
                health_increase = 1
                
                pancakes -= 1
                dialogue = random.choice(loc.l(f'nikogotchi.dialogue.{nikogotchi.original_name}.fed'))
                
        await nikogotchi_data.update(
            pancakes = pancakes,
            golden_pancakes = golden_pancakes,
            glitched_pancakes = glitched_pancakes
        )

        nikogotchi.hunger = min(50, nikogotchi.hunger + hunger_increase)
        nikogotchi.health = min(50, nikogotchi.health + health_increase)

        await self.save_nikogotchi(nikogotchi, ctx.author.id)

        buttons = self.nikogotchi_buttons(ctx.author.id, ctx.locale)
        select = await self.feed_nikogotchi(ctx)

        embed = await self.get_main_nikogotchi_embed(ctx.locale, await self.get_nikogotchi_age(ctx.author.id),
                                                     dialogue, [], nikogotchi)

        await ctx.edit_origin(embed=embed, components=[ActionRow(select), ActionRow(*buttons)])

    @nikogotchi.subcommand(sub_cmd_description='Send away your Nikogotchi.')
    async def send_away(self, ctx: SlashContext):
        
        loc = Localization(ctx.locale)

        nikogotchi = await self.get_nikogotchi(ctx.author.id)
        
        if nikogotchi is None:
            return await fancy_message(ctx, loc.l('nikogotchi.other.you_invalid'), ephemeral=True, color=0xff0000)
        
        name = nikogotchi.name

        buttons = [
            Button(style=ButtonStyle.RED, label=loc.l('general.buttons._yes'), custom_id=f'rehome {ctx.author.id}')
        ]

        embed = await fancy_embed(loc.l('nikogotchi.other.send_away.description', name=name))
        embed.set_footer(text=loc.l('nikogotchi.other.send_away.footer'))

        await ctx.send(embed=embed, ephemeral=True, components=buttons)

        button = await self.bot.wait_for_component(components=buttons)
        button_ctx = button.ctx

        custom_id = button_ctx.custom_id

        if custom_id == f'rehome {ctx.author.id}':
            
            await self.delete_nikogotchi(ctx.author.id)

            embed = await fancy_embed(loc.l('nikogotchi.other.send_away.success', name=name))

            await ctx.edit(embed=embed, components=[])

    @nikogotchi.subcommand(sub_cmd_description='Rename your Nikogotchi.')
    @slash_option('name', description='Rename your Nikogotchi.', opt_type=OptionType.STRING, required=True)
    async def rename(self, ctx: SlashContext, name):

        nikogotchi = await self.get_nikogotchi(ctx.author.id)
        
        loc = Localization(ctx.locale)

        if nikogotchi is None:
            return await fancy_message(ctx, loc.l('nikogotchi.other.you_invalid'), ephemeral=True, color=0xff0000)

        old_name = nikogotchi.name
        nikogotchi.name = name

        await self.save_nikogotchi(nikogotchi, ctx.author.id)
        await fancy_message(ctx, f'[ Successfully renamed **{old_name}** to **{nikogotchi.name}**! ]', ephemeral=True)

    @nikogotchi.subcommand(sub_cmd_description='Show off your Nikogotchi, or view someone else\'s.!')
    @slash_option('user', description='The user to view.', opt_type=OptionType.USER, required=True)
    async def show(self, ctx: SlashContext, user: User):

        uid = user.id

        nikogotchi = await self.get_nikogotchi(uid)
        
        loc = Localization(ctx.locale)

        if nikogotchi is None:
            return await fancy_message(ctx, loc.l('nikogotchi.other.other_invalid'), ephemeral=True, color=0xff0000)

        age = await self.get_nikogotchi_age(uid)

        embed = Embed(
            title=nikogotchi.name,
            color=0x8b00cc,
        )

        embed.author = EmbedAuthor(
            name=f'Owned by {user.username}',
            icon_url=user.avatar.url
        )

        embed.description = str(loc.l('nikogotchi.other.view.description', years=age.years, months=age.months, days=age.days, health=nikogotchi.health))

        embed.set_image(url=f'https://cdn.discordapp.com/emojis/{nikogotchi.emoji}.png?v=1')

        await ctx.send(embed=embed)

    @nikogotchi.subcommand(sub_cmd_description='Trade your Nikogotchi with someone else!')
    @slash_option('user', description='The user to trade with.', opt_type=OptionType.USER, required=True)
    async def trade(self, ctx: SlashContext, user: User):

        nikogotchi_one = await self.get_nikogotchi(ctx.author.id)
        nikogotchi_two = await self.get_nikogotchi(user.id)
        
        loc = Localization(ctx.locale)
        
        if nikogotchi_one is None:
            return await fancy_message(ctx, loc.l('nikogotchi.other.you_invalid'), ephemeral=True, color=0xff0000)
        if nikogotchi_two is None:
            return await fancy_message(ctx, loc.l('nikogotchi.other.other_invalid'), ephemeral=True, color=0xff0000)

        await fancy_message(ctx, loc.l('nikogotchi.other.trade.waiting', user=user.mention), ephemeral=True)

        uid = user.id

        embed = await fancy_embed(loc.l('nikogotchi.other.trade.request', user=ctx.author.mention, icon_one=nikogotchi_one.emoji, icon_two=nikogotchi_two.emoji, name_one=nikogotchi_one.name, name_two=nikogotchi_two.name))

        buttons = [
            Button(style=ButtonStyle.SUCCESS, label=loc.l('general.buttons._yes'), custom_id=f'trade {ctx.author.id} {uid}'),
            Button(style=ButtonStyle.DANGER, label=loc.l('general.buttons._no'), custom_id=f'decline {ctx.author.id} {uid}')
        ]

        await user.send(embed=embed, components=buttons)

        button = await self.bot.wait_for_component(components=buttons)
        button_ctx = button.ctx

        await button_ctx.defer(edit_origin=True)

        custom_id = button_ctx.custom_id

        if custom_id == f'trade {ctx.author.id} {uid}':
            await self.save_nikogotchi(nikogotchi_two, ctx.author.id)
            await self.save_nikogotchi(nikogotchi_one, uid)

            embed_two = await fancy_embed(loc.l('nikogotchi.other.trade.success', user=user.mention, name=nikogotchi_two.name))
            embed_two.set_image(url=f'https://cdn.discordapp.com/emojis/{nikogotchi_two.emoji}.png?v=1')

            embed_one = await fancy_embed(loc.l('nikogotchi.other.trade.success', user=ctx.author.mention, name=nikogotchi_one.name))
            embed_one.set_image(url=f'https://cdn.discordapp.com/emojis/{nikogotchi_one.emoji}.png?v=1')

            await button_ctx.edit_origin(embed=embed_one, components=[])
            await ctx.edit(embed=embed_two)
        else:
            embed = await fancy_embed(loc.l('nikogotchi.other.trade.declined'))
            await ctx.edit(embed=embed)

            embed = await fancy_embed(loc.l('nikogotchi.other.trade.success_decline'))

            await button_ctx.edit_origin(embed=embed, components=[])

    @slash_command(description='View the treasure you currently have, or someone else\'s!')
    @slash_option('user', description='The user to view.', opt_type=OptionType.USER, required=True)
    async def treasure(self, ctx: SlashContext, user: User):
        embed = Embed(
            title=str(Localization(ctx.locale).l('treasure.title', user=user.username)),
            color=0x8b00cc,
        )

        all_treasures = await fetch_treasure()
        treasure_string = ''
        
        user_data: UserData = await UserData(user.id).fetch()
        owned_treasures = user_data.owned_treasures

        for treasure_nid, item in all_treasures.items():
            
            treasure_loc: dict = Localization(ctx.locale).l(f'items.treasures')
            
            name = treasure_loc[treasure_nid]['name']
            
            treasure_string += f'<:emoji:{item["image"]}> {name}: **{owned_treasures.get(treasure_nid, 0)}x**\n\n'

        embed.description = str(Localization(ctx.locale).l('treasure.description', user=user.mention, treasure=treasure_string))

        await ctx.send(embed=embed)
