from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import Data.capsule_characters as chars
import aiohttp
import aiofiles
import json
import textwrap
import database as db
from interactions import PartialEmoji, User

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

    for character in chars.get_characters():
        emoji = PartialEmoji(id=character.emoji)
        shop_images.append(f'https://cdn.discordapp.com/emojis/{emoji.id}.webp?size=96&quality=lossless')

    wool_ = await DownloadImage('https://cdn.discordapp.com/emojis/1044668364422918176.png', 'wool')
    sun_ = await DownloadImage('https://cdn.discordapp.com/emojis/1026207773559619644.png', 'sun')

    for item in images:
        img = await DownloadImage(item, 'icon')
        img = img.convert('RGBA')
        img = img.resize((25, 25), Image.Resampling.NEAREST)
        icons.append(img)
    for item in shop_images:
        img = await DownloadImage(item, 'icon')
        img = img.convert('RGBA')
        img = img.resize((25, 33), Image.Resampling.NEAREST)
        shop_icons.append(img)


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

    profile_background = await db.get('user_data', user_id, 'equipped_background')
    profile_description = await db.get('user_data', user_id, 'profile_description')
    user_badges = await db.get('user_data', user_id, 'unlocked_badges')
    shop_badges = await db.get('user_data', user_id, 'unlocked_nikogotchis')
    profile_description = profile_description.strip("'")

    bgs = await open_backgrounds()

    get_profile_background = bgs['background'][profile_background]

    bg = await DownloadImage(get_profile_background['image'], 'background')

    fnt = ImageFont.truetype("font/TerminusTTF-Bold.ttf", 25)  # Font
    fnt_small = ImageFont.truetype("font/TerminusTTF-Bold.ttf", 20)  # Font
    title_fnt = ImageFont.truetype("font/TerminusTTF-Bold.ttf", 25)  # Font

    d = ImageDraw.Draw(bg)

    d.text((42, 32), msg, font=title_fnt, fill=(252, 186, 86), stroke_width=1, stroke_fill=0xffb829)

    description = textwrap.fill(profile_description, 35)

    d.text((210, 140), f"\"{description}\"", font=fnt, fill=(255, 255, 255), stroke_width=2, stroke_fill=0x000000)

    pfp = await DownloadImage(user_pfp, 'profile_picture')

    pfp = pfp.resize((148, 148))

    bg.paste(pfp, (42, 80), pfp.convert('RGBA'))

    init_index = 390
    index = init_index
    i = 0
    pos_y = 320

    current_badge_id = 0

    for icon in shop_icons:
        i += 1

        enhancer = ImageEnhance.Brightness(icon)
        icon = enhancer.enhance(0)

        if current_badge_id in shop_badges:
            icon = enhancer.enhance(1)

        bg.paste(icon, (index, pos_y), icon.convert('RGBA'))
        index += 30

        # loop through until we get to the end of the maximum amount of badges to show horizontally
        if (i > 8):
            index = init_index
            pos_y += 30
            i = 0

        current_badge_id += 1

    init_index = 55
    index = init_index
    i = 0
    pos_y = 320

    current_badge_id = 0

    height_index = 0

    for icon in icons:
        i += 1

        # ! I don't know what the fuck this means, what the hell were you on, past axiinyaa
        # * after a small amount of debugging i think i understand now, but it is still so stupid but i'm too lazy to refactor teehee

        enhancer = ImageEnhance.Brightness(icon)
        icon = enhancer.enhance(0)

        if current_badge_id in user_badges:
            icon = enhancer.enhance(1)

        bg.paste(icon, (index, pos_y), icon.convert('RGBA'))
        index += 30

        # loop through until we get to the end of the maximum amount of badges to show horizontally
        if (i > 4):

            if height_index == 3:
                pos_y = 290
                init_index = 220

            index = init_index
            pos_y += 30

            height_index += 1
            i = 0

        current_badge_id += 1

    coins = await db.get('user_data', user_id, 'wool')
    sun = await db.get('user_data', user_id, 'suns')
    d.text((648, 250), f'{coins} x', font=fnt, fill=(255, 255, 255), anchor='rt', align='right', stroke_width=2,
           stroke_fill=0x000000)
    bg.paste(wool_, (659, 243), wool_.convert('RGBA'))

    d.text((648, 32), f'{sun} x', font=fnt, fill=(255, 255, 255), anchor='rt', align='right', stroke_width=2,
           stroke_fill=0x000000)
    bg.paste(sun_, (659, 25), sun_.convert('RGBA'))

    d.text((42, 251), 'Unlocked Items:', font=fnt, fill=(255, 255, 255), stroke_width=2, stroke_fill=0x000000)

    d.text((50, 290), 'Achievements:', font=fnt_small, fill=(255, 255, 255), stroke_width=1, stroke_fill=0x000000)
    d.text((385, 290), 'Nikogotchis:', font=fnt_small, fill=(255, 255, 255), stroke_width=1, stroke_fill=0x000000)

    bg.save('Images/Profile Viewer/result.png')


async def DownloadImage(image_url, filename):
    async with aiohttp.ClientSession() as session:
        async with session.get(image_url) as resp:
            if resp.status == 200:
                f = await aiofiles.open(f'Images/Profile Viewer/{filename}.png', mode='wb')
                await f.write(await resp.read())
                await f.close()

    return Image.open(f'Images/Profile Viewer/{filename}.png')