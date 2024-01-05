from dataclasses import dataclass
from datetime import datetime
from database import Database
import re
    
@dataclass
class UserData:
    
    async def update(self, **what: str):
        data_dict = await Database.update_user(self.p_key, self.__dict__, **what)
        self = UserData(**data_dict)
        return self
        
    p_key: int
    wool: int
    suns: int
    equipped_bg: str
    profile_description: str
    badge_notifications: bool
    owned_treasures: dict
    owned_backgrounds: list[str]
    owned_badges: list[str]
    ask_limit: int
    last_asked: datetime
    times_asked: int
    times_transmitted: int
    times_shattered: int
    wool_gained: int
    suns_gained: int
    
async def fetch_user(id: int, as_dict: bool = False):
    data = await Database.fetch('UserData', id)
    
    if as_dict:
        return data
    else:
        return UserData(**data)