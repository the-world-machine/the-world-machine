from interactions import Embed, slash_command, SlashContext, SlashCommand, slash_option
from Localization.Localization import loc
from database import Database
from datetime import datetime, timedelta

async def nikogotchi_check(ctx: SlashContext):
    
    nikogotchi_data = await Database.fetch('nikogotchi_data', 'data', ctx.author.id)
    last_reminder = await Database.fetch('nikogotchi_data', 'last_reminder_date', ctx.author.id)
    
    duration = datetime.now() - last_reminder
    
    if nikogotchi_data is not None and duration > timedelta(hours=12):
        
        await Database.update('nikogotchi_data', 'last_reminder_date', ctx.author.id, datetime.now())
        
        if duration > timedelta(days=1):
            embed = Embed(description=f'[ Reminder to take care of <:any:{nikogotchi_data["emoji"]}>**{nikogotchi_data["name"]}** {ctx.author.mention}! ]')
            embed.color = 0x2f3136
            embed.set_footer(text='Use /nikogotchi check to check up on your Nikogotchi!')
            
            return embed
    

def twm_cmd(description = 'This is a command.', ephemeral = False):

    def decorator(func):
        
        @slash_command(name=func.__name__, description=description)
        async def wrapper(ctx: SlashCommand, *args, **kwargs):
            
            context: SlashContext = args[0]
            
            await context.defer(ephemeral=ephemeral)
            
            nikogotchi_reminder = await nikogotchi_check(context)
            
            command: SlashCommand = await func(ctx, *args, **kwargs)
            
            if nikogotchi_reminder is not None:
                await context.send(embed=nikogotchi_reminder, ephemeral=True)
            
            return command

        return wrapper
    
    return decorator

def twm_subcmd(command: SlashCommand, description = 'This is a subcommand.', ephemeral = False):
    
    def decorator(func):
        @command.subcommand(sub_cmd_name=func.__name__, sub_cmd_description=description)
        async def wrapper(ctx: SlashCommand, *args, **kwargs):
            
            context: SlashContext = args[0]
            
            await context.defer(ephemeral=ephemeral)
            
            nikogotchi_reminder = await nikogotchi_check(context)
            
            command: SlashCommand = await func(ctx, *args, **kwargs)
            
            if nikogotchi_reminder is not None:
                await context.send(embed=nikogotchi_reminder, ephemeral=True)
            
            return command
        
        return wrapper
    
    return decorator