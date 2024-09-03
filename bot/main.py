
from interactions import *
from interactions.api.events import MemberAdd, Ready
import interactions.ext.prefixed_commands as prefixed_commands

from database import ServerData, create_connection
from config_loader import *
import load_commands
import os
import random
import utilities.profile.profile_viewer as view
from modules.textbox import TextboxModule

print('\nStarting The World Machine... 1/4')
intents = Intents.DEFAULT | Intents.MESSAGE_CONTENT | Intents.MESSAGES | Intents.GUILD_MEMBERS | Intents.GUILDS

client = Client(
    intents=intents,
    disable_dm_commands=True,
    send_command_tracebacks=False
)

prefixed_commands.setup(client, default_prefix='*')

print("\nLoading Commands... 2/3")

load_commands.load_commands(client)

async def pick_avatar():
    get_avatars = os.listdir('bot/images/profile_pictures')
    random_avatar = random.choice(get_avatars)

    avatar = File('bot/images/profile_pictures/' + random_avatar)

    await client.user.edit(avatar=avatar)


@listen(Ready)
async def on_ready():
    
    ### space for testing
    # return
    ### space for testing
    
    print("\nFinalizing... 3/3")
    
    create_connection()
    
    print('Database Connected')

    await client.change_presence(status=Status.ONLINE, activity=Activity(type=ActivityType.PLAYING, name='OneShot'))
    await view.load_badges()

    if client.user.id == 1015629604536463421:
        await pick_avatar()
    else:
        try:
            await client.user.edit(avatar=File('bot/images/unstable.png'))
        except:
            pass
        
    print("\n----------------------------------------")
    print("\nThe World Machine is ready!\n\n")

# Whenever a user joins a guild...
@listen(MemberAdd)
async def on_guild_join(event: MemberAdd):
    
    # If not the main bot don't send welcome messages.
    if client.user.id != 1015629604536463421:
        return
    
    if event.member.bot:
        return
    
    # Check to see if we should generate a welcome message
    server_data: ServerData = await ServerData(event.guild_id).fetch()
    
    if not server_data.welcome_message:
        return

    # Generate welcome textbox.
    await TextboxModule.generate_welcome_message(event.guild, event.member, server_data.welcome_message)

client.start(load_config('token'))