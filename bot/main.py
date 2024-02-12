import asyncio

from interactions import *
from interactions.api.events import MessageCreate, MemberAdd, Ready, GuildJoin
import interactions.ext.prefixed_commands as prefixed_commands

from database import ServerData, create_connection
from config_loader import *
import load_commands
import os
import random
import utilities.profile.profile_viewer as view
import utilities.profile.badge_manager as badge_manager
import utilities.fetch_capsule_characters as chars
from localization.loc import load_languages

from modules.textbox import TextBoxGeneration

from utilities.shop.fetch_shop_data import fetch_shop_data

print('\nStarting The World Machine... 1/4')
intents = Intents.DEFAULT | Intents.MESSAGE_CONTENT | Intents.MESSAGES | Intents.GUILD_MEMBERS | Intents.GUILDS

client = Client(
    intents=intents,
    disable_dm_commands=True,
    send_command_tracebacks=False
)

prefixed_commands.setup(client, default_prefix='*')

print("\nLoading Commands... 2/4")

load_commands.load_commands(client)

print('\nLoading Additional Extensions... 3/4')

client.load_extension("interactions.ext.sentry", token=load_config('sentry'))  # Debugging and errors.

async def pick_avatar():
    get_avatars = os.listdir('bot/image/profile_pictures')
    random_avatar = random.choice(get_avatars)

    avatar = File('bot/images/profile_pictures' + random_avatar)

    await client.user.edit(avatar=avatar)


@listen(Ready)
async def on_ready():
    print("\nFinalizing... 4/4")
    
    create_connection()
    
    print('Database Connected')

    await client.change_presence(status=Status.ONLINE, activity=Activity(type=ActivityType.WATCHING, name='over OneShot'))
    chars.get_characters()
    await view.load_badges()

    if client.user.id == 1015629604536463421:
        await pick_avatar()
    else:
        try:
            await client.user.edit(avatar=File('bot/image/unstable.png'))
        except:
            pass
        
    load_languages()
    
    print('Loaded Languages.')

    print("\n----------------------------------------")
    print("\nThe World Machine is ready!\n\n")

# Whenever a user joins a guild...
@listen(MemberAdd)
async def on_guild_join(event: MemberAdd):
    
    # If not the main bot, please don't send welcome messages.
    if client.user.id != 1015629604536463421:
        return
    
    # Check to see if we should generate a welcome message
    server_data: ServerData = await ServerData(event.guild_id).fetch()
    
    if not server_data.welcome_message:
        return

    # Generate welcome textbox.
    await TextBoxGeneration.generate_welcome_message(event.guild, event.member, server_data.welcome_message)

client.start(load_config('token'))