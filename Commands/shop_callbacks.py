from interactions import *
from Utilities.FetchShopData import fetch_shop_data
import database

shop = None


def setup_callbacks(command):
    global shop
    shop = command


class Callbacks(Extension):

    @component_callback('buy_pancakes_1', 'buy_pancakes_golden', 'buy_pancakes_glitched')
    async def buy_pancakes_callback(self, ctx: ComponentContext):

        data = await fetch_shop_data()
        pancake_data = data['Pancakes']
    
        await ctx.defer(edit_origin=True)
    
        wool = database.fetch('user_data', 'wool', ctx.author.id)
        pancakes = database.fetch('nikogotchi_data', 'pancakes', ctx.author.id)
        golden_pancakes = database.fetch('nikogotchi_data', 'golden_pancakes', ctx.author.id)
        custom_id = ctx.custom_id
    
        footer = ''
    
        if custom_id == 'buy_pancakes_1':
            if wool < pancake_data['Pancake']['cost']:
                footer = '[ You do not have enough wool to buy a pancake! ]'
            else:
                footer = '[ Successfully bought a pancake! ]'
                database.update('user_data', 'wool', ctx.author.id, wool - pancake_data['Pancake']['cost'])
                database.update('nikogotchi_data', 'pancakes', ctx.author.id, pancakes + 1)
    
        if custom_id == 'buy_pancakes_golden':
            if wool < pancake_data['Golden Pancake']['cost']:
                footer = '[ You do not have enough wool to buy a golden pancake! ]'
            else:
                footer = '[ Successfully bought a golden pancake! ]'
                database.update('user_data', 'wool', ctx.author.id, wool - pancake_data['Golden Pancake']['cost'])
                database.update('nikogotchi_data', 'golden_pancakes', ctx.author.id, golden_pancakes + 1)
    
        if custom_id == 'buy_pancakes_glitched':
            if wool < pancake_data['???']['cost']:
                footer = '[ You do not have enough wool to buy whatever this thing is! ]'
            else:
                footer = '[ Successfully bought... something? ]'
                database.update('user_data', 'wool', ctx.author.id, wool - pancake_data['???']['cost'])
                database.update('nikogotchi_data', 'glitched_pancakes', ctx.author.id, pancakes + 1)
    
        embed, buttons = await shop.get_pancakes(int(ctx.author.id))
    
        embed.set_footer(text=footer)
    
        await ctx.edit_origin(embed=embed, components=buttons)

    pages = [{"uid": 0, "page": 0}]
    
    @component_callback('move_left', 'move_right', 'buy_background')
    async def background_callbacks(self, ctx: ComponentContext):
    
        custom_id = ctx.custom_id
    
        i = 0
        for page in self.pages:
            if page['uid'] == str(ctx.author.id):
                break
    
            i += 1
    
        if i == len(self.pages):
            self.pages.append({'uid': str(ctx.author.id), 'page': 0})
            current_page = self.pages[-1]
            i = self.pages.index(current_page)
        else:
            current_page = self.pages[i]
    
        if custom_id == 'move_left':
    
            if current_page['page'] <= 0:
                current_page['page'] = 2
            else:
                current_page['page'] -= 1
    
        if custom_id == 'move_right':
    
            if current_page['page'] >= 2:
                current_page['page'] = 0
            else:
                current_page['page'] += 1
    
        await shop.open_backgrounds(int(ctx.author.id), current_page['page'])
    
        footer = ''
    
        if custom_id == 'buy_background':
            background = shop.current_background_stock[current_page['page']]
            wool = database.fetch('user_data', 'wool', ctx.author.id)
    
            if wool < background['cost']:
                footer = "[ You don't have enough wool for this! ]"
            else:
                all_backgrounds = await shop.get_backgrounds()
    
                unlocked_background = database.fetch('user_data', 'unlocked_backgrounds', ctx.author.id)
    
                for i, bg in enumerate(all_backgrounds):
                    if bg['name'] == background['name']:
                        unlocked_background.append(i)
                        break
    
                database.update('user_data', 'wool', ctx.author.id, wool - background['cost'])
                database.update('user_data', 'unlocked_backgrounds', ctx.author.id, unlocked_background)
    
                footer = f'[ Successfully bought {background["name"]}! ]'
    
        embed, buttons = await shop.open_backgrounds(int(ctx.author.id), current_page['page'])
    
        embed.set_footer(footer)
    
        await ctx.edit_origin(embed=embed, components=buttons)

    @component_callback('buy_treasure_1', 'buy_treasure_2', 'buy_treasure_3', 'sell_treasures')
    async def treasure_callbacks(self, ctx: ComponentContext):
    
        custom_id = ctx.custom_id
    
        await shop.open_treasures(ctx.author.id)
    
        wool = database.fetch('user_data', 'wool', ctx.author.id)
        user_treasures = database.fetch('nikogotchi_data', 'treasure', ctx.author.id)
        get_treasures = shop.get_treasures()
    
        footer = ''
    
        treasure_1_price = get_treasures[shop.current_treasure_stock[0]]['price'] * shop.current_stock_price
        treasure_2_price = get_treasures[shop.current_treasure_stock[1]]['price'] * shop.current_stock_price
        treasure_3_price = get_treasures[shop.current_treasure_stock[2]]['price'] * shop.current_stock_price
    
        if custom_id == 'buy_treasure_1':
            if wool < treasure_1_price:
                footer = "[ You don't have enough wool for this! ]"
            else:
                user_treasures[shop.current_treasure_stock[0]] += 1
                database.update('nikogotchi_data', 'treasure', ctx.author.id, user_treasures)
                database.update('user_data', 'wool', ctx.author.id, wool - treasure_1_price)
                footer = f'[ Successfully bought {get_treasures[shop.current_treasure_stock[0]]["name"]}! ]'
    
        if custom_id == 'buy_treasure_2':
            if wool < treasure_2_price:
                footer = "[ You don't have enough wool for this! ]"
            else:
                user_treasures[shop.current_treasure_stock[1]] += 1
                database.update('nikogotchi_data', 'treasure', ctx.author.id, user_treasures)
                database.update('user_data', 'wool', ctx.author.id, wool - treasure_2_price)
                footer = f'[ Successfully bought {get_treasures[shop.current_treasure_stock[1]]["name"]}! ]'
    
        if custom_id == 'buy_treasure_3':
            if wool < treasure_3_price:
                footer = "[ You don't have enough wool for this! ]"
            else:
                user_treasures[shop.current_treasure_stock[2]] += 1
                database.update('nikogotchi_data', 'treasure', ctx.author.id, user_treasures)
                database.update('user_data', 'wool', ctx.author.id, wool - treasure_3_price)
                footer = f'[ Successfully bought {get_treasures[shop.current_treasure_stock[2]]["name"]}! ]'
    
        if custom_id != 'sell_treasures':
            embed, components = await shop.open_treasures(ctx.author.id)
        else:
            embed, components = await shop.open_sell_treasures(ctx.author.id)
    
        embed.set_footer(text=footer)
    
        await ctx.edit_origin(embed=embed, components=components)

    @component_callback('sell_treasures_menu')
    async def sell_treasures_menu(self, ctx: ComponentContext):
    
        value = int(ctx.values[0])
    
        wool = database.fetch('user_data', 'wool', ctx.author.id)
        user_treasures = database.fetch('nikogotchi_data', 'treasure', ctx.author.id)
        get_treasures = shop.get_treasures()
    
        footer = ''
    
        if user_treasures[value] == 0:
            footer = "[ You don't have any treasures to sell! ]"
        else:
            user_treasures[value] -= 1
            database.update('nikogotchi_data', 'treasure', ctx.author.id, user_treasures)
            database.update('user_data', 'wool', ctx.author.id, wool + get_treasures[value]['price'] * shop.current_stock_price)
    
            footer = f'[ Successfully sold {get_treasures[value]["name"]}! ]'
    
        embed, components = await shop.open_sell_treasures(ctx.author.id)
    
        embed.set_footer(text=footer)
    
        await ctx.edit_origin(embed=embed, components=components)

    @component_callback('buy_blue', 'buy_green', 'buy_red', 'buy_yellow')
    async def capsule_callbacks(self, ctx: ComponentContext):

        shop_data = await fetch_shop_data()
        capsule_data = shop_data['Capsules']

        custom_id = ctx.custom_id

        wool = database.fetch('user_data', 'wool', ctx.author.id)

        footer = ''

        if custom_id == 'buy_blue':
            if wool < capsule_data['Blue Capsule']['cost']:
                footer = "[ You don't have enough wool for this! ]"
            else:
                database.update('user_data', 'wool', ctx.author.id, wool - capsule_data['Blue Capsule']['cost'])
                database.update('nikogotchi_data', 'nikogotchi_available', ctx.author.id, database.fetch('nikogotchi_data', 'nikogotchi_available', ctx.author.id) + 1)
                database.update('nikogotchi_data', 'rarity', ctx.author.id, 0)
                footer = f'[ Successfully bought a Blue Capsule! ]'

        if custom_id == 'buy_green':
            if wool < capsule_data['Green Capsule']['cost']:
                footer = "[ You don't have enough wool for this! ]"
            else:
                database.update('user_data', 'wool', ctx.author.id, wool - capsule_data['Green Capsule']['cost'])
                database.update('nikogotchi_data', 'nikogotchi_available', ctx.author.id, database.fetch('nikogotchi_data', 'nikogotchi_available', ctx.author.id) + 1)
                database.update('nikogotchi_data', 'rarity', ctx.author.id, 1)
                footer = f'[ Successfully bought a Green Capsule! ]'

        if custom_id == 'buy_red':
            if wool < capsule_data['Red Capsule']['cost']:
                footer = "[ You don't have enough wool for this! ]"
            else:
                database.update('user_data', 'wool', ctx.author.id, wool - capsule_data['Red Capsule']['cost'])
                database.update('nikogotchi_data', 'nikogotchi_available', ctx.author.id, database.fetch('nikogotchi_data', 'nikogotchi_available', ctx.author.id) + 1)
                database.update('nikogotchi_data', 'rarity', ctx.author.id, 2)
                footer = f'[ Successfully bought a Red Capsule! ]'

        if custom_id == 'buy_yellow':
            if wool < capsule_data['Yellow Capsule']['cost']:
                footer = "[ You don't have enough wool for this! ]"
            else:
                database.update('user_data', 'wool', ctx.author.id, wool - capsule_data['Yellow Capsule']['cost'])
                database.update('nikogotchi_data', 'nikogotchi_available', ctx.author.id, database.fetch('nikogotchi_data', 'nikogotchi_available', ctx.author.id) + 1)
                database.update('nikogotchi_data', 'rarity', ctx.author.id, 3)
                footer = f'[ Successfully bought a Yellow Capsule! ]'

        embed, components = await shop.get_capsules(ctx.author.id)

        embed.set_footer(text=footer)

        await ctx.edit_origin(embed=embed, components=components)

    @component_callback('go_back')
    async def go_back(self, ctx: ComponentContext):
        embed, buttons = await shop.get_main_shop(int(ctx.author.id))
        await ctx.edit_origin(embed=embed, components=buttons)