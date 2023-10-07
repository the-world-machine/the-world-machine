# Import the necessary modules
from interactions.ext.prefixed_commands import prefixed_command, PrefixedContext
from interactions import Extension
import database as db
from load_data import load_config
import requests


class DevCommands(Extension):
    allowed_users = [302883948424462346]

    @prefixed_command()
    async def add_wool(self, ctx: PrefixedContext, target: int, amount: int):
        # Check if the user is allowed to use this command

        if ctx.author.id not in self.allowed_users:
            return

        # Fetch the target user
        target_user = await ctx.client.fetch_user(target)

        wool = db.get('user_data', target, 'wool')

        db.update('user_data', 'wool', target, wool + amount)

        await ctx.send(f'Successfully added {amount} wool to {target_user.mention}. <@{ctx.author.id}>')

    # Define the "set_wool" command using the new system
    @prefixed_command()
    async def set_wool(self, ctx: PrefixedContext, target: int, amount: int):
        # Check if the user is allowed to use this command

        if ctx.author.id not in self.allowed_users:
            return

        # Fetch the target user
        target_user = await ctx.client.fetch_user(target)

        db.update('user_data', 'wool', target, amount)

        await ctx.send(f'Successfully set wool to {amount} for {target_user.mention}. {ctx.author.mention}')

    # Define the "add_badge" command using the new system
    @prefixed_command()
    async def add_badge(self, ctx: PrefixedContext, target: int, badge_id: int):
        # Check if the user is allowed to use this command

        if ctx.author.id not in self.allowed_users:
            return

        # Fetch the target user
        target_user = await ctx.client.fetch_user(target)

        badges = db.get('user_data', target, 'unlocked_badges')
        badges.append(badge_id)

        db.update('user_data', 'unlocked_badges', target, badges)

        await ctx.send(f'Successfully added badge with id {badge_id} to {target_user.mention}. <@{ctx.author.id}>')

    # Define the "remove_badge" command using the new system
    @prefixed_command()
    async def remove_badge(self, ctx: PrefixedContext, target: int, badge_id: int):
        # Check if the user is allowed to use this command

        if ctx.author.id not in self.allowed_users:
            return

        # Fetch the target user
        target_user = await ctx.client.fetch_user(target)

        badges = db.get('user_data', target, 'unlocked_badges')

        if badge_id in badges:
            badges.remove(badge_id)

        db.update('user_data', 'unlocked_badges', target, badges)

        await ctx.send(f'Successfully removed badge with id {badge_id} from {target_user.mention}. <@{ctx.author.id}>')

    # Define the "restart" command using the new system
    @prefixed_command()
    async def restart(self, ctx: PrefixedContext):
        # Check if the user is allowed to use this command

        if ctx.author.id not in self.allowed_users:
            return

        await ctx.send('Restarting.')

        API_KEY = "Bearer " + load_config('SPARKED')

        header = {"Authorization": API_KEY}
        r = requests.post('https://control.sparkedhost.us/api/client/servers/92aeea52/power',
                          json={"signal": "restart"}, headers=header)
        print(r.status_code)

    # Define the "stop" command using the new system
    @prefixed_command()
    async def stop(self, ctx: PrefixedContext):
        # Check if the user is allowed to use this command

        if ctx.author.id not in self.allowed_users:
            return

        await ctx.send('Stopping.')

        API_KEY = "Bearer " + load_config('SPARKED')

        header = {"Authorization": API_KEY}
        r = requests.post('https://control.sparkedhost.us/api/client/servers/92aeea52/power',
                          json={"signal": "stop"}, headers=header)
        print(r.status_code)
