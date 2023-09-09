import json
import random

from interactions import *
from interactions.api.events import Component
from Utilities.fancysend import *
from Utilities.bot_icons import loading
import Data.capsule_characters as chars
import database

from datetime import datetime
from dateutil import relativedelta

from Utilities.bot_icons import loading


class Command(Extension):

    buttons = [
        Button(
            style=ButtonStyle.SUCCESS,
            label='Feed',
            custom_id=f'feed'
        ),
        Button(
            style=ButtonStyle.SUCCESS,
            label='Pet',
            custom_id=f'pet'
        ),
        Button(
            style=ButtonStyle.SUCCESS,
            label='Clean',
            custom_id=f'clean'
        ),
        Button(
            style=ButtonStyle.PRIMARY,
            label='Find Treasure',
            custom_id=f'find_treasure'
        ),
        Button(
            style=ButtonStyle.GREY,
            emoji=PartialEmoji(id=1147696088250335303),
            custom_id=f'refresh'
        )
    ]

    async def get_nikogotchi_age(self, uid: int):
        date_hatched_str = await database.get('nikogotchi_data', uid, 'hatched')
        date_hatched = datetime.strptime(date_hatched_str, '%Y-%m-%d %H:%M:%S')

        return relativedelta.relativedelta(datetime.now(), date_hatched)

    async def get_main_nikogotchi_embed(self, uid: int, age: relativedelta.relativedelta, dialogue: str, found_treasure=[]):
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

        progress_bar_length = 5

        status = await database.get('nikogotchi_data', uid, 'nikogotchi_status')
        name = await database.get('nikogotchi_data', uid, 'name')
        health = await database.get('nikogotchi_data', uid, 'health')
        hunger = await database.get('nikogotchi_data', uid, 'hunger')
        attention = await database.get('nikogotchi_data', uid, 'attention')
        cleanliness = await database.get('nikogotchi_data', uid, 'cleanliness')
        emoji = await database.get('nikogotchi_data', uid, 'emoji')
        pancakes = await database.get('nikogotchi_data', uid, 'pancakes')

        health_value = round((health / 50) * progress_bar_length)
        hunger_value = round((hunger / 50) * progress_bar_length)
        attention_value = round((attention / 50) * progress_bar_length)
        cleanliness_value = round((cleanliness / 50) * progress_bar_length)

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
            title=name,
            color=0x8b00cc
        )

        nikogotchi_status = 'Your Nikogotchi seems to be doing okay.'
        if hunger < 30:
            nikogotchi_status = f'{name} seems quite hungry.'
        if attention < 30:
            nikogotchi_status = f'{name} seems quite lonely.'
        if cleanliness < 30:
            nikogotchi_status = f'{name} seems quite dirty.'

        if status == 3:
            nikogotchi_status = f'{name} is currently finding treasures!'

        if len(found_treasure) > 0:

            treasures = ''
            looked_over_treasures = []

            for index in found_treasure:

                if index in looked_over_treasures:
                    continue

                with open('Data/treasure.json', 'r') as f:
                    data = f.read()

                get_treasure = json.loads(data)
                treasure = get_treasure[index]

                treasures += f'<:any:{treasure["emoji"]}> {treasure["name"]} x{found_treasure.count(index)}\n'
                looked_over_treasures.append(index)

            nikogotchi_status = f'''
            {name} found some treasures!
            
            {treasures}
            '''

        if health < 30:
            nikogotchi_status = f'It seems {name} is in poor health.'

        embed.description = f'''
                    {nikogotchi_status}

                    **Health:** {health_progress_bar} ({health} / 50)

                    **Hunger:**      {hunger_progress_bar} ({hunger} / 50)
                    **Attention:**   {attention_progress_bar} ({attention} / 50)
                    **Cleanliness:** {cleanliness_progress_bar} ({cleanliness} / 50)
                    
                    **Age:** {age.years} years, {age.months} months, {age.days} days
                    
                    <:pancakes:1147281411854839829> {pancakes}
                    '''

        embed.set_image(url=f'https://cdn.discordapp.com/emojis/{emoji}.png')
        embed.set_footer(text=dialogue)

        return embed

    @slash_command(description="All things about your Nikogotchi!")
    async def nikogotchi(self, ctx: SlashContext):
        pass

    @nikogotchi.subcommand(sub_cmd_description="Check out your Nikogotchi!")
    async def check(self, ctx: SlashContext):

        uid = ctx.author.id

        rarity = await database.get('nikogotchi_data', ctx.author.id, 'rarity')
        status = await database.get('nikogotchi_data', ctx.author.id, 'nikogotchi_status')

        nikogotchi: chars.Nikogotchi

        if status >= 2:

            nikogotchi = chars.Nikogotchi(
                name=await database.get('nikogotchi_data', ctx.author.id, 'name'),
                emoji=await database.get('nikogotchi_data', ctx.author.id, 'emoji'),
                pancake_dialogue=await database.get('nikogotchi_data', ctx.author.id, 'pancake_dialogue'),
                pet_dialogue=await database.get('nikogotchi_data', ctx.author.id, 'pet_dialogue'),
                cleaned_dialogue=await database.get('nikogotchi_data', ctx.author.id, 'cleaned_dialogue'),
                rarity=rarity
            )

            await fancy_message(ctx, f'[ Loading Nikogotchi... {loading()} ]', ephemeral=True)

        else:

            viable_nikogotchi = []

            if status == 0:
                await fancy_message(ctx, "[ You don't have a Nikogotchi! You can buy a capsule from the shop to unlock a random one! ]",
                                    ephemeral=True, color=0xff0000)
                return

            nikogotchi_list = chars.get_characters()

            for character in nikogotchi_list:
                if rarity == character.rarity.value:
                    viable_nikogotchi.append(character)

            selected_nikogotchi = random.choice(viable_nikogotchi)

            owned_nikogotchi = await database.get('user_data', ctx.author.id, 'unlocked_nikogotchis')
            owned_nikogotchi.append(nikogotchi_list.index(selected_nikogotchi))
            await database.set('user_data', 'unlocked_nikogotchis', ctx.author.id, owned_nikogotchi)

            await database.set('nikogotchi_data', 'name', ctx.author.id, selected_nikogotchi.name)

            await database.set('nikogotchi_data', 'last_interacted', ctx.author.id,
                               datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S'))
            await database.set('nikogotchi_data', 'hatched', ctx.author.id,
                               datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S'))

            await database.set('nikogotchi_data', 'emoji', ctx.author.id, selected_nikogotchi.emoji)
            await database.set('nikogotchi_data', 'nikogotchi_status', ctx.author.id, 2)

            await database.set('nikogotchi_data', 'pancake_dialogue', ctx.author.id,
                               selected_nikogotchi.pancake_dialogue)
            await database.set('nikogotchi_data', 'pet_dialogue', ctx.author.id, selected_nikogotchi.pet_dialogue)
            await database.set('nikogotchi_data', 'cleaned_dialogue', ctx.author.id,
                               selected_nikogotchi.cleaned_dialogue)

            await database.set('nikogotchi_data', 'health', ctx.author.id, 50)
            await database.set('nikogotchi_data', 'hunger', ctx.author.id, 50)
            await database.set('nikogotchi_data', 'attention', ctx.author.id, 50)
            await database.set('nikogotchi_data', 'cleanliness', ctx.author.id, 50)

            nikogotchi = selected_nikogotchi

            hatched_embed = Embed(
                title=f'You found {selected_nikogotchi.name}!',
                color=0x8b00cc,
                description='Do you want to give them a new name?'
            )

            hatched_embed.set_footer(text='Dismiss this message and then rerun the command to keep the current name.')

            hatched_embed.set_image(url=f'https://cdn.discordapp.com/emojis/{selected_nikogotchi.emoji}.png')

            buttons = [
                Button(style=ButtonStyle.GREEN, label='Yes', custom_id=f'yes {ctx.author.id}'),
                Button(style=ButtonStyle.RED, label='No', custom_id=f'no {ctx.author.id}')
            ]

            message = await ctx.send(embed=hatched_embed, components=buttons, ephemeral=True)

            button: Component = await self.bot.wait_for_component(components=buttons)
            button_ctx = button.ctx

            custom_id = button_ctx.custom_id

            if custom_id == f'yes {ctx.author.id}':
                modal = Modal(
                    ShortText(
                        custom_id='name',
                        value=selected_nikogotchi.name,
                        label='Name'
                    ),
                    custom_id='name',
                    title='Give your Nikogotchi a name!',
                )

                await button_ctx.send_modal(modal)

                modal_ctx: ModalContext = await self.bot.wait_for_modal(modal)

                await modal_ctx.defer(edit_origin=True)

                selected_nikogotchi.name = await database.set('nikogotchi_data', 'name', ctx.author.id, modal_ctx.kwargs['name'])

        await self.load_nikogotchi(nikogotchi, ctx, uid)

    async def load_nikogotchi(self, nikogotchi: chars.Nikogotchi, ctx: SlashContext, uid: int):

        health = await database.get('nikogotchi_data', uid, 'health')
        hunger = await database.get('nikogotchi_data', uid, 'hunger')
        attention = await database.get('nikogotchi_data', uid, 'attention')
        cleanliness = await database.get('nikogotchi_data', uid, 'cleanliness')

        pancakes = await database.get('nikogotchi_data', uid, 'pancakes')

        age = await self.get_nikogotchi_age(int(ctx.author.id))

        last_interacted_str = await database.get('nikogotchi_data', ctx.author.id, 'last_interacted')
        last_interacted = datetime.strptime(last_interacted_str, '%Y-%m-%d %H:%M:%S')

        # Get the current datetime
        current_time = datetime.now()

        # Calculate the time difference in hours
        time_difference = (current_time - last_interacted).total_seconds() / 3600

        modifier = 1

        status = await database.get('nikogotchi_data', uid, 'nikogotchi_status')

        if status == 3:
            modifier = 1.2

        new_hunger = int(max(0, hunger - time_difference * modifier))
        new_attention = int(max(0, attention - time_difference * 1.8 * modifier))
        new_cleanliness = int(max(0, cleanliness - time_difference * 1.25 * modifier))

        await database.set('nikogotchi_data', 'hunger', ctx.author.id, new_hunger)
        await database.set('nikogotchi_data', 'attention', ctx.author.id, new_attention)
        await database.set('nikogotchi_data', 'cleanliness', ctx.author.id, new_cleanliness)

        new_health = int(health)

        if new_hunger <= 0 or new_attention <= 0 or new_cleanliness <= 0:
            new_health = health - time_difference
            await database.set('nikogotchi_data', 'health', ctx.author.id, new_health)

        if new_health <= 0:
            embed = Embed(
                title=f'{nikogotchi.name} Passed away...',
                color=0x696969,
                description=f'''
                {nikogotchi.name} lived a full life of {age.years} years, {age.months} months, and {age.days} days.
                Hours since last taken care of: **{int(time_difference)} Hours**

                Nikogotchis rely on your love and attention, so keep trying to give them the best care possible!
                '''
            )

            buttons = []
            await database.set('nikogotchi_data', 'nikogotchi_status', ctx.author.id, 0)
        else:
            embed = await self.get_main_nikogotchi_embed(uid, age, '...')

            self.buttons[0].disabled = False
            self.buttons[1].disabled = False
            self.buttons[2].disabled = False

            self.buttons[3].label = 'Find Treasure'
            self.buttons[3].custom_id = 'find_treasure'

            buttons = self.buttons

            embed.set_image(url=f'https://cdn.discordapp.com/emojis/{nikogotchi.emoji}.png')

            if status == 3:

                treasures_found = []

                for i in range(int(time_difference)):
                    value = random.randint(0, 1000)
                    treasure = -1
                    if value > 0:
                        treasure = random.choice([0, 1, 2])
                    if value > 600:
                        treasure = random.choice([3, 4, 5])
                    if value > 900:
                        treasure = random.choice([6, 7, 8])

                    treasures_found.append(treasure)

                    user_treasures = await database.get('nikogotchi_data', uid, 'treasure')
                    user_treasures[treasure] += 1
                    await database.set('nikogotchi_data', 'treasure', uid, user_treasures)

                self.buttons[0].disabled = True
                self.buttons[1].disabled = True
                self.buttons[2].disabled = True

                self.buttons[3].label = 'Call Nikogotchi Back'
                self.buttons[3].custom_id = 'call_back'

                buttons = self.buttons

                embed = await self.get_main_nikogotchi_embed(uid, age, '...', treasures_found)
                embed.set_image(url='')

        await ctx.edit(embed=embed, components=buttons)

    @component_callback('feed', 'pet', 'clean', 'find_treasure', 'refresh', 'call_back')
    async def nikogotchi_interaction(self, ctx: ComponentContext):

        await ctx.defer(edit_origin=True)

        pancakes = await database.get('nikogotchi_data', ctx.author.id, 'pancakes')

        pancake_dialogue = await database.get('nikogotchi_data', ctx.author.id, 'pancake_dialogue')
        pet_dialogue = await database.get('nikogotchi_data', ctx.author.id, 'pet_dialogue')
        cleaned_dialogue = await database.get('nikogotchi_data', ctx.author.id, 'cleaned_dialogue')
        emoji = await database.get('nikogotchi_data', ctx.author.id, 'emoji')
        status = await database.get('nikogotchi_data', ctx.author.id, 'nikogotchi_status')
        age = await self.get_nikogotchi_age(int(ctx.author.id))

        last_interacted_str = await database.get('nikogotchi_data', ctx.author.id, 'last_interacted')
        last_interacted = datetime.strptime(last_interacted_str, '%Y-%m-%d %H:%M:%S')

        # Get the current datetime
        current_time = datetime.now()

        # Calculate the time difference in hours
        time_difference = (current_time - last_interacted).total_seconds() / 3600

        custom_id = ctx.custom_id

        await database.set('nikogotchi_data', 'last_interacted', ctx.author.id, datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S'))

        dialogue = '...'

        if custom_id == 'feed':
            if pancakes <= 0:
                dialogue = 'You don\'t have any pancakes! Buy some from the shop to feed your Nikogotchi!'
            else:

                pancakes = await database.set('nikogotchi_data', 'pancakes', ctx.author.id, pancakes - 1)

                # Adjust hunger, attention, and cleanliness
                hunger_increase = 25

                current_hunger = await database.get('nikogotchi_data', ctx.author.id, 'hunger')

                new_hunger = min(50, current_hunger + hunger_increase)

                hunger = await database.set('nikogotchi_data', 'hunger', ctx.author.id, new_hunger)

                dialogue = random.choice(pancake_dialogue)

        if custom_id == 'pet':
            # Adjust hunger, attention, and cleanliness
            attention_increase = 20

            current_attention = await database.get('nikogotchi_data', ctx.author.id, 'attention')

            new_attention = min(50, current_attention + attention_increase)

            attention = await database.set('nikogotchi_data', 'attention', ctx.author.id, new_attention)

            dialogue = random.choice(pet_dialogue)

        if custom_id == 'clean':
            cleanliness_increase = 30

            current_cleanliness = await database.get('nikogotchi_data', ctx.author.id, 'cleanliness')

            new_cleanliness = min(50, current_cleanliness + cleanliness_increase)

            cleanliness = await database.set('nikogotchi_data', 'cleanliness', ctx.author.id, new_cleanliness)

            dialogue = random.choice(cleaned_dialogue)

        if custom_id == 'find_treasure':
            dialogue = 'Your Nikogotchi is now finding treasure! Come back later or call them back now to see what loot they found!'
            status = await database.set('nikogotchi_data', 'nikogotchi_status', ctx.author.id, 3)

        if custom_id == 'call_back':
            status = await database.set('nikogotchi_data', 'nikogotchi_status', ctx.author.id, 2)

        embed = await self.get_main_nikogotchi_embed(int(ctx.author.id), age, dialogue)

        self.buttons[0].disabled = False
        self.buttons[1].disabled = False
        self.buttons[2].disabled = False

        self.buttons[3].label = 'Find Treasure'
        self.buttons[3].custom_id = 'find_treasure'

        buttons = self.buttons

        embed.set_image(url=f'https://cdn.discordapp.com/emojis/{emoji}.png')

        if status == 3:

            treasures_found = []

            for i in range(int(time_difference)):
                value = random.randint(0, 1000)
                treasure = -1
                if value > 0:
                    treasure = random.choice([0, 1, 2])
                if value > 600:
                    treasure = random.choice([3, 4, 5])
                if value > 900:
                    treasure = random.choice([6, 7, 8])

                treasures_found.append(treasure)

                user_treasures = await database.get('user_data', ctx.author.id, 'treasures')
                user_treasures[treasure] += 1
                await database.set('user_data', 'treasures', ctx.author.id, user_treasures)

            self.buttons[0].disabled = True
            self.buttons[1].disabled = True
            self.buttons[2].disabled = True

            self.buttons[3].label = 'Call Nikogotchi Back'
            self.buttons[3].custom_id = 'call_back'

            buttons = self.buttons

            embed = await self.get_main_nikogotchi_embed(ctx.author.id, age, '...', treasures_found)
            embed.set_image(url='')

        await ctx.edit_origin(embed=embed, components=buttons)

    @nikogotchi.subcommand(sub_cmd_description='Send away your Nikogotchi.')
    async def send_away(self, ctx: SlashContext):

        status = await database.get('nikogotchi_data', ctx.author.id, 'nikogotchi_status')

        if not status >= 2:
            return await fancy_message(ctx, "[ You don't have a Nikogotchi! ]", ephemeral=True, color=0xff0000)

        name = await database.get('nikogotchi_data', ctx.author.id, 'name')

        buttons = [
            Button(style=ButtonStyle.RED, label='Yes', custom_id=f'rehome {ctx.author.id}')
        ]

        embed = await fancy_embed(f'[ Are you sure you want to send away {name} so that you can adopt a new one? ]')
        embed.set_footer(text='Dismiss this message if you change your mind.')

        await fancy_message(ctx, f'[ Are you sure you want to send away {name} so that you can adopt a new one? ]', ephemeral=True, components=buttons)

        button = await self.bot.wait_for_component(components=buttons)
        button_ctx = button.ctx

        custom_id = button_ctx.custom_id

        if custom_id == f'rehome {ctx.author.id}':
            await database.set('nikogotchi_data', 'nikogotchi_status', ctx.author.id, 0)

            embed = await fancy_embed(f'[ Successfully sent away {name}. Enjoy your future Nikogotchi! ]')

            await ctx.edit(embed=embed, components=[])

    @nikogotchi.subcommand(sub_cmd_description='Rename your Nikogotchi.')
    @slash_option('name', description='Rename your Nikogotchi.', opt_type=OptionType.STRING, required=True)
    async def rename(self, ctx: SlashContext, name):

        status = await database.get('nikogotchi_data', ctx.author.id, 'nikogotchi_status')

        if not status >= 2:
            return await fancy_message(ctx, "[ You don't have a Nikogotchi! ]", ephemeral=True, color=0xff0000)

        old_name = await database.get('nikogotchi_data', ctx.author.id, 'name')
        new_name = await database.set('nikogotchi_data', 'name', ctx.author.id, name)

        await fancy_message(ctx, f'[ Successfully renamed **{old_name}** to **{new_name}**! ]')

    @nikogotchi.subcommand(sub_cmd_description='Show off your Nikogotchi, or view someone else\'s.!')
    @slash_option('user', description='The user to view.', opt_type=OptionType.USER, required=True)
    async def show(self, ctx: SlashContext, user: User):

        uid = user.id

        status = await database.get('nikogotchi_data', uid, 'nikogotchi_status')

        if status < 2:
            return await fancy_message(ctx, "[ This person doesn't seem to have a Nikogotchi! ]", ephemeral=True, color=0xff0000)

        name = await database.get('nikogotchi_data', uid, 'name')
        age = await self.get_nikogotchi_age(uid)
        emoji = await database.get('nikogotchi_data', uid, 'emoji')

        embed = Embed(
            title=f'{name}',
            color=0x8b00cc,
        )

        embed.author = EmbedAuthor(
            name=f'Owned by {ctx.author.username}',
            icon_url=ctx.author.avatar_url
        )

        embed.description = f'''
        Age: {age.years} years, {age.months} months, and {age.days} days.
        
        Health: {await database.get('nikogotchi_data', uid, 'health')}/50
        <:dfd:1147281411854839829> {await database.get('nikogotchi_data', uid, 'pancakes')}
        '''

        embed.set_image(url=f'https://cdn.discordapp.com/emojis/{emoji}.png?v=1')

        await ctx.send(embed=embed)

    @nikogotchi.subcommand(sub_cmd_description='Trade your Nikogotchi with someone else!')
    @slash_option('user', description='The user to trade with.', opt_type=OptionType.USER, required=True)
    async def trade(self, ctx: SlashContext, user: User):

        one_status = await database.get('nikogotchi_data', ctx.author.id, 'nikogotchi_status')
        two_status = await database.get('nikogotchi_data', user.id, 'nikogotchi_status')

        if not one_status >= 2:
            return await fancy_message(ctx, "[ You don't have a Nikogotchi! ]", ephemeral=True, color=0xff0000)

        if not two_status >= 2:
            return await fancy_message(ctx, "[ This person doesn't seem to have a Nikogotchi! ]", ephemeral=True, color=0xff0000)

        await fancy_message(ctx, f'[ Sent {user.mention} a trade offer! Waiting on their response... {loading()} ]', ephemeral=True)

        one_name = await database.get('nikogotchi_data', ctx.author.id, 'name')
        one_emoji = await database.get('nikogotchi_data', ctx.author.id, 'emoji')
        one_health = await database.get('nikogotchi_data', ctx.author.id, 'health')
        one_pancake_dialogue = await database.get('nikogotchi_data', ctx.author.id, 'pancake_dialogue')
        one_attention_dialogue = await database.get('nikogotchi_data', ctx.author.id, 'pet_dialogue')
        one_cleaned_dialogue = await database.get('nikogotchi_data', ctx.author.id, 'cleaned_dialogue')
        one_hatched = await database.get('nikogotchi_data', ctx.author.id, 'hatched')

        two_name = await database.get('nikogotchi_data', user.id, 'name')
        two_emoji = await database.get('nikogotchi_data', user.id, 'emoji')
        two_health = await database.get('nikogotchi_data', user.id, 'health')
        two_pancake_dialogue = await database.get('nikogotchi_data', user.id, 'pancake_dialogue')
        two_attention_dialogue = await database.get('nikogotchi_data', user.id, 'pet_dialogue')
        two_cleaned_dialogue = await database.get('nikogotchi_data', user.id, 'cleaned_dialogue')
        two_hatched = await database.get('nikogotchi_data', user.id, 'hatched')

        uid = user.id

        embed = await fancy_embed(f'**{ctx.author.username}** wants to trade their Nikogotchi with you!\n\nName: {one_name}\nHealth: {one_health}/50\n\nDo you want to trade **{two_name}**?')
        embed.set_image(url=f'https://cdn.discordapp.com/emojis/{one_emoji}.png?v=1')

        buttons = [
            Button(style=ButtonStyle.SUCCESS, label='Trade', custom_id=f'trade {ctx.author.id} {uid}'),
            Button(style=ButtonStyle.DANGER, label='Decline', custom_id=f'decline {ctx.author.id} {uid}')
        ]

        await user.send(embed=embed, components=buttons)

        button = await self.bot.wait_for_component(components=buttons)
        button_ctx = button.ctx

        await button_ctx.defer(edit_origin=True)

        custom_id = button_ctx.custom_id

        if custom_id == f'trade {ctx.author.id} {uid}':
            await database.set('nikogotchi_data', 'name', ctx.author.id, two_name)
            await database.set('nikogotchi_data', 'emoji', ctx.author.id, two_emoji)
            await database.set('nikogotchi_data', 'health', ctx.author.id, two_health)
            await database.set('nikogotchi_data', 'pancake_dialogue', ctx.author.id, two_pancake_dialogue)
            await database.set('nikogotchi_data', 'pet_dialogue', ctx.author.id, two_attention_dialogue)
            await database.set('nikogotchi_data', 'cleaned_dialogue', ctx.author.id, two_cleaned_dialogue)
            await database.set('nikogotchi_data', 'hatched', ctx.author.id, two_hatched)

            await database.set('nikogotchi_data', 'hunger', ctx.author.id, 50)
            await database.set('nikogotchi_data', 'attention', ctx.author.id, 50)
            await database.set('nikogotchi_data', 'cleanliness', ctx.author.id, 50)

            await database.set('nikogotchi_data', 'name', uid, one_name)
            await database.set('nikogotchi_data', 'emoji', uid, one_emoji)
            await database.set('nikogotchi_data', 'health', uid, one_health)
            await database.set('nikogotchi_data', 'pancake_dialogue', uid, one_pancake_dialogue)
            await database.set('nikogotchi_data', 'pet_dialogue', uid, one_attention_dialogue)
            await database.set('nikogotchi_data', 'cleaned_dialogue', uid, one_cleaned_dialogue)
            await database.set('nikogotchi_data', 'hatched', uid, one_hatched)

            await database.set('nikogotchi_data', 'hunger', uid, 50)
            await database.set('nikogotchi_data', 'attention', uid, 50)
            await database.set('nikogotchi_data', 'cleanliness', uid, 50)

            embed_two = await fancy_embed(f'[ Successfully traded with {user.mention}! Say hello to **{two_name}**! ]')
            embed_two.set_image(url=f'https://cdn.discordapp.com/emojis/{two_emoji}.png?v=1')

            embed_one = await fancy_embed(f'[ Successfully traded with **{ctx.author.username}**! Say hello to **{one_name}**! ]')
            embed_one.set_image(url=f'https://cdn.discordapp.com/emojis/{one_emoji}.png?v=1')

            await button_ctx.edit_origin(embed=embed_one, components=[])
            await ctx.edit(embed=embed_two)
        else:
            embed = await fancy_embed(f'[ {user.mention} declined your trade offer. ]')
            await ctx.edit(embed=embed)

            embed = await fancy_embed(f'[ Successfully declined trade offer. ]')

            await button_ctx.edit_origin(embed=embed, components=[])

    @slash_command(description='View the treasure you currently have, or someone else\'s!')
    @slash_option('user', description='The user to view.', opt_type=OptionType.USER, required=True)
    async def treasure(self, ctx: SlashContext, user: User):
        embed = Embed(
            title=f'{user.username}\'s Treasure',
            color=0x8b00cc,
        )

        with open('Data/treasure.json', 'r') as f:
            data = f.read()

        treasure = json.loads(data)
        treasure_string = ''

        user_treasure = await database.get('nikogotchi_data', user.id, 'treasure')

        for i, item in enumerate(treasure):
            treasure_string += f'<:emoji:{item["emoji"]}> {item["name"]}: **{user_treasure[i]}x**\n\n'

        embed.description = f'''
        Here is {user.mention}'s treasure!
        
        {treasure_string}
        Earn more treasure through Nikogotchis or purchasing them from the shop!
        '''

        await ctx.send(embed=embed)
