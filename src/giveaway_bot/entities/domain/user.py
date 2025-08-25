from dataclasses import dataclass
from datetime import datetime

from giveaway_bot.entities.enum.language import Language
from giveaway_bot.entities.enum.role import Role


@dataclass
class User:
    id: int
    tg_id: int
    username: str | None
    role: Role
    language: Language
    is_banned: bool
    is_active: bool
    is_subscribed: bool
    was_subscribed: bool
    created_at: datetime

    def active(self):
        return self.is_active and not self.is_banned

@dataclass
class UserAction:
    tg_id: int
    giveaway_id: str
    action: str
    created_at: datetime
