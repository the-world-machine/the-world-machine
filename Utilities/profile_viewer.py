import json
import textwrap

import aiofiles
import aiohttp
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
from interactions import PartialEmoji, User

import database as db

icons = []
shop_icons = []

wool_ = None
sun_ = None


async def load_badges():
    global wool_
    global sun_

    print('Loading Badges...')

    images = []
    shop_images = []

    badges = await open_badges()

    for stamp in badges['Badges']:
        emoji = PartialEmoji(id=stamp['emoji'])
        images.append(f'https://cdn.discordapp.com/emojis/{emoji.id}.webp?size=96&quality=lossless')

    wool_ = await DownloadImage('https://cdn.discordapp.com/emojis/1044668364422918176.png', 'wool')
    sun_ = await DownloadImage('https://cdn.discordapp.com/emojis/1026207773559619644.png', 'sun')

    for item in images:
        img = await DownloadImage(item, 'icon')
        img = img.convert('RGBA')
        img = img.resize((35, 35), Image.NEAREST)
        icons.append(img)


async def open_badges():
    async with aiofiles.open('Data/badges.json', 'r') as f:
        strdata = await f.read()

    return json.loads(strdata)


async def open_backgrounds():
    async with aiofiles.open('Data/backgrounds.json', 'r') as f:
        strdata = await f.read()

    return json.loads(strdata)


async def DrawBadges(ctx, user: User):
    print('Viewing Badges...')

    msg = f'{user.username}\'s Profile'

    user_id = user.id
    user_pfp = user.avatar_url

    profile_background = db.fetch('user_data', 'equipped_background', user_id)
    profile_description = db.fetch('user_data', 'profile_description', user_id)
    user_badges = db.fetch('user_data', 'unlocked_badges', user_id)
    profile_description = profile_description.strip("'")

    bgs = await open_backgrounds()

    get_profile_background = bgs['background'][profile_background]

    bg = await DownloadImage(get_profile_background['image'], 'background')

    fnt = ImageFont.truetype("font/TerminusTTF-Bold.ttf", 25)  # Font
    title_fnt = ImageFont.truetype("font/TerminusTTF-Bold.ttf", 25)  # Font

    d = ImageDraw.Draw(bg)

    d.text((42, 32), msg, font=title_fnt, fill=(252, 186, 86), stroke_width=1, stroke_fill=0xffb829)

    description = textwrap.fill(profile_description, 35)

    d.text((210, 140), f"\"{description}\"", font=fnt, fill=(255, 255, 255), stroke_width=2, stroke_fill=0x000000)

    pfp = await DownloadImage(user_pfp, 'profile_picture')

    pfp = pfp.resize((148, 148))

    bg.paste(pfp, (42, 80), pfp.convert('RGBA'))

    init_x = 60  # Start with the first column (adjust as needed)
    init_y = 310

    x = init_x
    y = init_y

    x_increment = 45
    y_increment = 50

    current_row = 0
    current_column = 1

    for i, icon in enumerate(icons):
        enhancer = ImageEnhance.Brightness(icon)
        icon = enhancer.enhance(0)

        if i in user_badges:
            icon = enhancer.enhance(1)

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

    coins = db.fetch('user_data', 'wool', user_id)
    sun = db.fetch('user_data', 'suns', user_id)
    d.text((648, 70), f'{coins} x', font=fnt, fill=(255, 255, 255), anchor='rt', align='right', stroke_width=2,
           stroke_fill=0x000000)
    bg.paste(wool_, (659, 63), wool_.convert('RGBA'))

    d.text((648, 32), f'{sun} x', font=fnt, fill=(255, 255, 255), anchor='rt', align='right', stroke_width=2,
           stroke_fill=0x000000)
    bg.paste(sun_, (659, 25), sun_.convert('RGBA'))

    d.text((42, 251), 'Unlocked Achievements:', font=fnt, fill=(255, 255, 255), stroke_width=2, stroke_fill=0x000000)

    bg.save('Images/Profile Viewer/result.png')


async def DownloadImage(image_url, filename):
    async with aiohttp.ClientSession() as session:
        async with session.get(image_url) as resp:
            if resp.status == 200:
                f = await aiofiles.open(f'Images/Profile Viewer/{filename}.png', mode='wb')
                await f.write(await resp.read())
                await f.close()

    return Image.open(f'Images/Profile Viewer/{filename}.png')