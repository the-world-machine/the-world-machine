from dataclasses import dataclass
from datetime import datetime
from database import Database
import re
    
@dataclass
class UserData:
    
    async def update(self, **what: str):
        data_dict = await Database.update_table('UserData', self.p_key, self.__dict__, **what)
        self = UserData(**data_dict)
        return self
    
    async def increment_value(self, what: str, amount: int = 1):
        await Database.increment_value('UserData', what, self.p_key, amount)
        data_dict = self.__dict__
        
        data_dict[what] += amount
        
        return UserData(**data_dict)
        
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
    
@dataclass
class ServerData:

    async def update(self, **what: str):
        data_dict = await Database.update_table('ServerData', self.p_key, self.__dict__, **what)
        self = ServerData(**data_dict)
        return self
    
    p_key: int
    transmit_channel: int
    transmittable_servers: dict
    blocked_servers: list
    anonymous: bool
    transmit_images: bool
    
async def fetch_server(id: int, as_dict: bool = False):
    data = await Database.fetch('ServerData', id)
    
    if as_dict:
        return data
    else:
        return ServerData(**data)