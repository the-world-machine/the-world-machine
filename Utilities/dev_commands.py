# Import the necessary modules
import json
from interactions.ext.prefixed_commands import prefixed_command, PrefixedContext
from interactions import Extension
import database as db
from load_data import load_config
from importlib import reload, import_module
import aiohttp


class DevCommands(Extension):
    allowed_users = [302883948424462346]
    
    @prefixed_command()
    async def reload_file(self, ctx: PrefixedContext, file: str):
        # Check if the user is allowed to use this command

        if ctx.author.id not in self.allowed_users:
            return

        # Reload the file
        module = import_module(file)
        reload(module)
        
        await ctx.send("Successfully reloaded file.")
        
    @prefixed_command()
    async def reload_ext(self, ctx: PrefixedContext, ext: str):
        # Check if the user is allowed to use this command

        if ctx.author.id not in self.allowed_users:
            return

        # Reload the extension
        self.client.reload_extension(f'Commands.{ext}')
        
        await ctx.send("Successfully reloaded extension.")
    
    @prefixed_command()
    async def statistics(self, ctx: PrefixedContext, *statistics: str):
        # Check if the user is allowed to use this command

        if ctx.author.id not in self.allowed_users:
            return

        # Fetch the bot statistics from the JSON file
        with open('Data/bot_statistics.json', 'r') as f:
            bot_statistics = json.load(f)

        # Send the bot statistics as an embed
        
        text = ''
        
        for statistic in statistics:
            text += f'``{statistic}: {bot_statistics.get(statistic, "N/A")}``\n'
            
        await ctx.send(text)

    @prefixed_command()
    async def add_wool(self, ctx: PrefixedContext, target: int, amount: int):
        # Check if the user is allowed to use this command

        if ctx.author.id not in self.allowed_users:
            return

        # Fetch the target user
        target_user = await ctx.client.fetch_user(target)

        wool = await db.fetch('user_data', 'wool', target)

        await db.update('user_data', 'wool', target, wool + amount)

        await ctx.send(f'Successfully added {amount} wool to {target_user.mention}. <@{ctx.author.id}>')

    # Define the "set_wool" command using the new system
    @prefixed_command()
    async def set_wool(self, ctx: PrefixedContext, target: int, amount: int):
        # Check if the user is allowed to use this command

        if ctx.author.id not in self.allowed_users:
            return

        # Fetch the target user
        target_user = await ctx.client.fetch_user(target)

        await db.update('UserData', 'wool', target, amount)

        await ctx.send(f'Successfully set wool to {amount} for {target_user.mention}. {ctx.author.mention}')

    # Define the "add_badge" command using the new system
    @prefixed_command()
    async def add_badge(self, ctx: PrefixedContext, target: int, *badge_ids: str):
        # Check if the user is allowed to use this command
        
        badges = []
        
        for badge in badge_ids:
            badges.append(badge.replace('_', ' '))

        if ctx.author.id not in self.allowed_users:
            return

        # Fetch the target user
        target_user = await ctx.client.fetch_user(target)

        badges = await db.fetch('user_data', 'unlocked_badges', target)
        badges.append(badges)

        await db.update('UserData', 'unlocked_badges', target, badges)

        await ctx.send(f'Successfully added badge {badges} to {target_user.mention}. <@{ctx.author.id}>')

    # Define the "remove_badge" command using the new system
    @prefixed_command()
    async def remove_badge(self, ctx: PrefixedContext, target: int, *badge_ids: str):
        
        badges = []
        
        for badge in badge_ids:
            badges.append(badge.replace('_', ' '))
        # Check if the user is allowed to use this command

        if ctx.author.id not in self.allowed_users:
            return

        # Fetch the target user
        target_user = await ctx.client.fetch_user(target)

        owned_badges = await db.fetch('UserData', 'unlocked_badges', target)

        for b in owned_badges:
            if b in badges:
                badges.remove(b)

        await db.update('UserData', 'unlocked_badges', target, badges)

        await ctx.send(f'Successfully removed badge {badges} from {target_user.mention}. <@{ctx.author.id}>')

    # Define the "restart" command using the new system
    @prefixed_command()
    async def restart_(self, ctx: PrefixedContext):
        # Check if the user is allowed to use this command

        if ctx.author.id not in self.allowed_users:
            return

        await ctx.send('Restarting.')

        API_KEY = "Bearer " + load_config('SPARKED')

        header = {"Authorization": API_KEY}

        async with aiohttp.ClientSession() as session:
            async with session.request('POST','https://control.sparkedhost.us/api/client/servers/92aeea52/power', json={"signal": "restart"}, headers=header):
                print('Successfully Restarted.')

    # Define the "stop" command using the new system
    @prefixed_command()
    async def stop(self, ctx: PrefixedContext):
        # Check if the user is allowed to use this command

        if ctx.author.id not in self.allowed_users:
            return

        await ctx.send('Stopping.')

        API_KEY = "Bearer " + load_config('SPARKED')

        header = {"Authorization": API_KEY}

        async with aiohttp.ClientSession() as session:
            async with session.request('POST','https://control.sparkedhost.us/api/client/servers/92aeea52/power', json={"signal": "stop"}, headers=header):
                print('Successfully Stopped.')