from interactions import *
from utilities.fancy_send import *
from utilities.bot_icons import *
from localization.loc import Localization

class Command(Extension):
    
    async def open_interactions_select(self, locale: str, user: User):
        option_list = []
        
        localization = Localization(locale)
        
        interactions: dict[str, dict[str, str]] = localization.l('interact.options')
        
        user_mention = user.mention
        
        for id_, interaction in interactions.items():
            option_list.append(
                StringSelectOption(
                    label=interaction['name'],
                    value=f'{id_}_{user_mention}'
                )
            )
        
        return StringSelectMenu(
            *option_list,
            placeholder=localization.l('interact.placeholder'),
            custom_id='interaction_selected'
        )

    @slash_command()
    @slash_option(name='who', description='The users you want to do the action towards.', opt_type=OptionType.USER)
    async def interaction(self, ctx: SlashContext, who: User):
        '''Interact with other users in various ways.'''
        
        await self.start_interaction(ctx, who)
        
    @user_context_menu('💡 Interact...')
    async def interaction_context(self, ctx: ContextMenuContext):
        
        await self.start_interaction(ctx, ctx.target)
    
    async def start_interaction(self, ctx: SlashContext, who: User):
        
        loc = Localization(ctx.guild_locale)

        if ctx.author.id == who.id:
            await fancy_message(ctx, loc.l('interact.twm_is_fed_up_with_you', user=ctx.author.mention), ephemeral=True, color=0XFF0000)
            return
        
        if who.id == self.bot.user.id:
            await fancy_message(ctx, loc.l('interact.twm_not_being_very_happy', user=ctx.author.mention), ephemeral=True, color=0XFF0000)
            return
        
        if who.bot:
            await fancy_message(ctx, loc.l('interact.twm_questioning_if_youre_stupid_or_not', bot=who.mention, user=ctx.author.mention), ephemeral=True, color=0XFF0000)
            return
        
        menu = await self.open_interactions_select(ctx.guild_locale, who)
        
        localization = Localization(ctx.guild_locale)
        
        await ctx.send(content=localization.l('interact.selected', user=who.mention), components=menu, ephemeral=True)
    
    @component_callback('interaction_selected')
    async def menu_callback(self, ctx: ComponentContext):
        
        await ctx.defer(edit_origin=True)
        
        result = ctx.values[0].split('_')
        
        interaction = result[0]
        user = result[1]
        
        localization = Localization(ctx.guild_locale)
        
        action = localization.l(f'interact.options.{interaction}.action', user=user)
        
        result = f'[ {ctx.author.mention} {action} ]'
        
        await ctx.channel.send(result)