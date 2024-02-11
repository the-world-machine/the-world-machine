import asyncio
from datetime import datetime, timedelta
from interactions import *
from interactions.api.events import *
from utilities.fancy_send import *
from utilities.profile.badge_manager import increment_value
import utilities.bot_icons as bot_icons
import utilities.ai_text as ai
from database import UserData

class Command(Extension):

    @listen()
    async def ask(self, event: MessageCreate):
        
        message = event.message
        
        if not message.content.startswith(f'<@{self.bot.user.id}>'):
            return

        can_ask, limit = await self.check(message.author.id)

        if not can_ask and self.bot.user.id != 1028058097383641118:
           return await fancy_message(message.channel, "[ You cannot ask anymore questions, you have reached your limit of 15 responses for today! ]", color=0xff0000)
        
        await message.channel.trigger_typing()
        
        response: str = await ai.chat(self.bot.user.id, message)
        
        response = response.removeprefix('<@1028058097383641118>: ')
        
        response = response.strip('[]')
        
        dialogue = response.split('¦')
        
        for i, text in enumerate(dialogue):
            
            if i == 0:
                msg = await message.reply(content=f'[{text}]')
                continue
            
            await asyncio.sleep(1)
            
            await msg.reply(content=f'[{text}]')

    async def check(self, uid: int):

        user = await UserData(uid).fetch()
        now = datetime.now()

        if now < user.last_asked:
            if user.ask_limit <= 0:
                return False, user.ask_limit

            await user.update(ask_limit=user.ask_limit - 1)
            return True, user.ask_limit

        new_day = now + timedelta(days=1)
        
        await user.update(
            last_asked = new_day,
            ask_limit = 14
        )
        
        return True, 14
