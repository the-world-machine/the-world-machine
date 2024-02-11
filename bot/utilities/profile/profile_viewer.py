import io
import json
import random
import textwrap

import aiofiles
import aiohttp
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
from interactions import PartialEmoji, User
from utilities.shop.fetch_items import fetch_background, fetch_badge
from localization.loc import l_num

import database as db

icons = []
shop_icons = []

wool_icon = None
sun_icon = None
badges = {}

async def load_badges():
    global wool_icon
    global sun_icon
    global badges
    global icons

    images = []
    icons = []
    
    badges = await fetch_badge('all')

    for _, badge in badges.items():
        images.append(badge['image'])

    wool_icon = await GetImage('https://cdn.discordapp.com/emojis/1044668364422918176.png')
    sun_icon = await GetImage('https://cdn.discordapp.com/emojis/1026207773559619644.png')

    for image_url in images:
        img = await GetImage(image_url)
        img = img.convert('RGBA')
        img = img.resize((35, 35), Image.NEAREST)
        icons.append(img)
    
    print('Loaded Badges')


async def open_badges():
    async with aiofiles.open('bot/data/badges.json', 'r') as f:
        strdata = await f.read()

    return json.loads(strdata)


async def open_backgrounds():
    return await db.get_items('Backgrounds')


async def draw_badges(user: User):
    if wool_icon is None:
        await load_badges()

    msg = f'{user.username}\'s Profile'

    user_id = user.id
    user_pfp = user.avatar_url

    user_data = await db.UserData(user_id).fetch()

    get_profile_background = await fetch_background(user_data.equipped_bg)
    bg = await GetImage(get_profile_background['image'])

    fnt = ImageFont.truetype("bot/font/TerminusTTF-Bold.ttf", 25)  # Font
    title_fnt = ImageFont.truetype("bot/font/TerminusTTF-Bold.ttf", 25)  # Font

    d = ImageDraw.Draw(bg)

    d.text((42, 32), msg, font=title_fnt, fill=(252, 186, 86), stroke_width=2, stroke_fill=(0, 0, 0))

    description = textwrap.fill(user_data.profile_description, 35)

    d.text((210, 140), f"{description}", font=fnt, fill=(255, 255, 255), stroke_width=2, stroke_fill=0x000000, align='center')

    pfp = await GetImage(user_pfp)

    pfp = pfp.resize((148, 148))

    bg.paste(pfp, (42, 80), pfp.convert('RGBA'))

    init_x = 60  # Start with the first column (adjust as needed)
    init_y = 310  # Start with the first row (adjust as needed)

    x = init_x # x position of Stamp
    y = init_y # y position of Stamp

    x_increment = 45 # How much to move to the next column
    y_increment = 50 # How much to move down to the next row

    current_row = 0 # Keep track of the current row
    current_column = 1 # Keep track of the current column
    
    angle_amount = 20 # How much to rotate the icon by
    
    badge_keys = list(badges.keys())

    for i, icon in enumerate(icons):
        enhancer = ImageEnhance.Brightness(icon)
        icon = enhancer.enhance(0)

        if badge_keys[i] in user_data.owned_badges:
            icon = enhancer.enhance(1)
            
            # Rotate the icon by a small random angle (e.g., between -10 and 10 degrees)
            random_angle = random.uniform(-angle_amount, angle_amount)
            icon = icon.rotate(random_angle)

        bg.paste(icon, (x, y), icon)

        x += x_increment  # Move to the next column

        # If we have reached the end of a row
        if (i + 1) % 5 == 0:
            x = init_x  # Reset to the first column
            y += y_increment  # Move to the next row
            current_row += 1

        # If we have displayed all the rows, start the next one.
        if current_row == 3:
            init_x = (init_x + x_increment * 5) * current_column + 10

            x = init_x
            y = init_y

            current_column += 1
            current_row = 0

    coins = user_data.wool
    sun = user_data.suns
    d.text((648, 70), f'{l_num(coins)} x', font=fnt, fill=(255, 255, 255), anchor='rt', align='right', stroke_width=2,
           stroke_fill=0x000000)
    bg.paste(wool_icon, (659, 63), wool_icon.convert('RGBA'))

    d.text((648, 32), f'{l_num(sun)} x', font=fnt, fill=(255, 255, 255), anchor='rt', align='right', stroke_width=2,
           stroke_fill=0x000000)
    bg.paste(sun_icon, (659, 25), sun_icon.convert('RGBA'))

    d.text((42, 251), 'Unlocked Stamps:', font=fnt, fill=(255, 255, 255), stroke_width=2, stroke_fill=0x000000)

    bg.save('bot/images/profile_viewer/result.png')


async def GetImage(image_url):
    async with aiohttp.ClientSession() as session:
        async with session.get(image_url) as resp:
            image = io.BytesIO(await resp.read())
            return Image.open(image)