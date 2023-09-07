from interactions import *
from Utilities.fancysend import *
import random
import datetime
import Utilities.badge_manager as bm


class Command(Extension):
    explosion_image = [
        'https://st.depositphotos.com/1001877/4912/i/600/depositphotos_49123283-stock-photo-light-bulb-exploding-concept-of.jpg',
        'https://st4.depositphotos.com/6588418/39209/i/600/depositphotos_392090278-stock-photo-exploding-light-bulb-dark-blue.jpg',
        'https://st.depositphotos.com/1864689/1538/i/600/depositphotos_15388723-stock-photo-light-bulb.jpg',
        'https://st2.depositphotos.com/1001877/5180/i/600/depositphotos_51808361-stock-photo-light-bulb-exploding-concept-of.jpg',
        'https://static7.depositphotos.com/1206476/749/i/600/depositphotos_7492923-stock-photo-broken-light-bulb.jpg',
    ]

    random_message = [
        "oh no",
        "whoops",
        "nice",
        "good job",
        "we're doomed",
        "woah",
        "don't do that",
        "uh oh"
    ]

    sad_image = 'https://images-ext-1.discordapp.net/external/47E2RmeY6Ro21ig0pkcd3HaYDPel0K8CWf6jumdJzr8/https/i.ibb.co/bKG17c2/image.png'

    last_called = {}

    @slash_command(name='explode', description="💥💥💥💥💥💥💥💥")
    async def explode(self, ctx: SlashContext):
        user_id = ctx.user.id

        if user_id in self.last_called:
            elapsed_time = datetime.datetime.utcnow() - self.last_called[user_id]
            if elapsed_time.total_seconds() < 20:
                await fancy_message(ctx, f"[ Please do not spam this command. `{round(20 - elapsed_time.total_seconds(), ndigits=0)} seconds left.` ]", ephemeral=True, color=0xfc0000)
                return

        self.last_called[user_id] = datetime.datetime.utcnow()

        with open('Data/explosions.txt', 'r') as f:
            explosion_amount = int(f.read())

        random_number = random.randint(1, len(Command.explosion_image)) - 1
        random_sadness = random.randint(1, 100)

        sad = False

        if random_sadness == 40:
            sad = True

        if not sad:
            embed = Embed(description=' ')

            embed.set_author(name=f'{self.random_message[random.randint(0, len(self.random_message) - 1)]}')

            if explosion_amount == 69:
                embed.set_author(name='nice')
            if explosion_amount == 420:
                embed.set_author(name='nice')
            if explosion_amount == 42069:
                embed.set_author(name='nice')
            if explosion_amount == 69420:
                embed.set_author(name='nice')

            embed.set_image(url=Command.explosion_image[random_number])
            embed.set_footer(f'The Sun has been exploded {explosion_amount} times.')
        else:
            embed = Embed(title='...')
            embed.set_image(url=Command.sad_image)
            embed.set_footer(f'[ You killed niko. ]')

        with open('Data/explosions.txt', 'w') as f:
            f.write(str(explosion_amount + 1))

        if not sad:
            await bm.increment_value(ctx, 'times_shattered')

        await ctx.send(embed=embed)
