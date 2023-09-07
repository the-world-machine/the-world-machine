import database as db
from load_data import load_config
from interactions import *
import os
import requests


async def admin_command(raw_command: Message, client: Client):
    allowed_users = [302883948424462346]

    if int(raw_command.author.id) not in allowed_users:
        return

    if raw_command.content[0] != '*':
        return

    command_data = raw_command.content.split(' ')
    command_name = command_data[0].split('*')[1]

    try:
        arg_1 = command_data[1]
        arg_2 = command_data[2]
        arg_3 = command_data[3]
    except:
        pass

    if command_name == 'add_wool':
        wool = await db.get('user_data', int(arg_1), 'wool')

        await db.set('user_data', 'wool', int(arg_1), wool + int(arg_2))

        await raw_command.reply(f'Successfully added {int(arg_2)} wool to target user. <@{int(raw_command.author.id)}>')

    if command_name == 'set_wool':
        wool = await db.get('user_data', int(arg_1), 'wool')

        await db.set('user_data', 'wool', int(arg_1), int(arg_2))

        await raw_command.reply(
            f'Successfully set wool to {int(arg_2)} for target user. <@{int(raw_command.author.id)}>')

    if command_name == 'add_badge':
        badges = await db.get('user_data', int(arg_1), 'unlocked_badges')

        badges.append(int(arg_2))

        await db.set('user_data', 'unlocked_badges', int(arg_1), badges)

        await raw_command.reply(
            f'Successfully added badge with id {int(arg_2)} to target user. <@{int(raw_command.author.id)}>')

    if command_name == 'remove_badge':
        badges: list[int] = await db.get('user_data', int(arg_1), 'unlocked_badges')

        badges.remove(int(arg_2))

        await db.set('user_data', 'unlocked_badges', int(arg_1), badges)

        await raw_command.reply(
            f'Successfully removed badge with id {int(arg_2)} to target user. <@{int(raw_command.author.id)}>')

    if command_name == 'restart':
        await raw_command.reply('Restarting.')

        API_KEY = "Bearer " + load_config('SPARKED')

        header = {"Authorization": API_KEY}
        r = requests.post('https://control.sparkedhost.us/api/client/servers/92aeea52/power',
                          json={"signal": "restart"}, headers=header)
        print(r.status_code)
        return

    if command_name == 'stop':
        await raw_command.reply('Stopping.')

        API_KEY = "Bearer " + load_config('SPARKED')

        header = {"Authorization": API_KEY}
        r = requests.post('https://control.sparkedhost.us/api/client/servers/92aeea52/power', json={"signal": "stop"},
                          headers=header)
        print(r.status_code)
        return