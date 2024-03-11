from interactions import *
from utilities.fancy_send import *
from utilities.bot_icons import *
from localization.loc import l, assign_variables

class Command(Extension):
    
    async def open_interactions_select(self, locale: str, user_mention: str):
        option_list = []
        
        interactions: dict[str, dict[str, str]] = l(locale, 'interact.options')
        
        if user_mention == self.bot.user.mention:
            user_mention = 'me'
        
        for id_, interaction in interactions.items():
            option_list.append(
                StringSelectOption(
                    label=interaction['name'],
                    value=f'{id_}_{user_mention}'
                )
            )
        
        return StringSelectMenu(
            *option_list,
            placeholder=l(locale, 'interact.placeholder'),
            custom_id='interaction_selected'
        )

    @slash_command()
    @slash_option(name='who', description='The users you want to do the action towards.', opt_type=OptionType.USER)
    async def interact(self, ctx: SlashContext, who: User):
        '''Interact with other users in various ways.'''
        
        menu = await self.open_interactions_select(ctx.guild_locale, who.mention)
        
        await ctx.send(content=l(ctx.guild_locale, 'interact.selected', user=who.mention), components=menu, ephemeral=True)
    
    @component_callback('interaction_selected')
    async def menu_callback(self, ctx: ComponentContext):
        result = ctx.values[0].split('_')
        
        interaction = result[0]
        user = result[1]
        
        action = l(ctx.guild_locale, f'interact.options.{interaction}.action', user=user)
        
        await ctx.channel.send(
            f'[ {ctx.author.mention} {action} ]'
        )