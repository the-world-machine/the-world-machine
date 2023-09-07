import database as db
from interactions import *
import aiofiles
import json


async def open_badges():
    async with aiofiles.open('Data/badges.json', 'r') as f:
        strdata = await f.read()

    return json.loads(strdata)


async def buy_badge(ctx: Message, badge_id: int, target: User):
    channel = await ctx.get_channel()

    badge_data = await open_badges()
    badge = badge_data['shop'][badge_id]

    badge_list = await db.get('user_data', target.id, 'unlocked_shop_badges')

    badge_list.append(badge_id)

    await db.set('user_data', 'unlocked_shop_badges', target.id, badge_list)

    emoji = PartialEmoji(id=badge['emoji'])

    text = f'[ {target.mention}, you successfully bought the <:{emoji.name}:{emoji.id}> **{badge["name"]}** badge for<:wool:1044668364422918176>**{badge["requirement"]}**! ]'

    embed = Embed(
        title='You got a badge!',
        description=text,
        color=0x8b00cc,
    )

    return await channel.send(embeds=embed)


async def earn_badge(ctx: GuildChannel, badge_id: int, target: User, send_message: bool = True):
    channel = ctx

    badge_data = await open_badges()
    badge = badge_data['Badges'][badge_id]

    badge_list = await db.get('user_data', target.id, 'unlocked_badges')

    badge_list.append(badge_id)

    await db.set('user_data', 'unlocked_badges', target.id, badge_list)

    emoji = PartialEmoji(id=badge['emoji'])

    type_descrim = {
        'shop': f', bought the <:{emoji.name}:{emoji.id}> **{badge["name"]}** for<:wool:1044668364422918176>**{badge["requirement"]}**!',
        'times_messaged': f' earned the <:{emoji.name}:{emoji.id}> **{badge["name"]}** by sending a message **{badge["requirement"]}** times!',
        'times_shattered': f' earned the <:{emoji.name}:{emoji.id}> **{badge["name"]}** by shattering a lightbulb **{badge["requirement"]}** times!',
        'times_asked': f' earned the <:{emoji.name}:{emoji.id}> **{badge["name"]}** by bothering The World Machine **{badge["requirement"]}** times!',
        'wool': f' earned the <:{emoji.name}:{emoji.id}> **{badge["name"]}** by earning over **{badge["requirement"]}** wool!',
        'times_transmitted': f' earned the <:{emoji.name}:{emoji.id}> **{badge["name"]}** by transmitting **{badge["requirement"]}** times!',
        'suns': f' earned the <:{emoji.name}:{emoji.id}> **{badge["name"]}** by giving/earning **{badge["requirement"]}** suns!'
    }

    embed = Embed(
        title='You got a badge!',
        description=f'<@{int(target.id)}>{type_descrim[badge["type"]]}',
        color=0x8b00cc
    )

    embed.set_footer('You can change this notification using "/settings badge_notifications"')

    can_notify = await db.get('user_data', target.id, 'unlock_notifications')

    if (badge['type'] == 'shop' or can_notify) and send_message:
        return await channel.send(embeds=embed)


async def check_wool_value(ctx: SlashContext, wool_amount: int):
    get_badges = await open_badges()
    get_badges = get_badges['Badges']

    guild = ctx.channel

    if guild.type == ChannelType.DM:
        return

    get_user_badges = await db.get('user_data', ctx.author.id, 'unlocked_badges')

    for i, badge in enumerate(get_badges):
        if badge['type'] == 'wool':
            if i in get_user_badges:
                continue

            if wool_amount < badge['requirement']:
                continue

            return await earn_badge(ctx, i, ctx.author, True)


async def increment_value(ctx: SlashContext, value_to_increment: str, target: User = None):
    get_badges = await open_badges()
    get_badges = get_badges['Badges']

    guild = ctx.channel

    if guild.type == ChannelType.DM:
        return

    if target:
        user = target
    else:
        user = ctx.author

    get_user_badges = await db.get('user_data', user.id, 'unlocked_badges')

    if get_user_badges is None:
        return

    await db.increment_value('user_data', value_to_increment, user.id)
    get_value = await db.get('user_data', user.id, value_to_increment)

    for i, badge in enumerate(get_badges):
        if badge['type'] == value_to_increment:
            if i in get_user_badges:
                continue

            if get_value < badge['requirement']:
                continue

            send_message = True

            if get_value > badge['requirement']:
                send_message = False

            return await earn_badge(guild, i, user, send_message)
