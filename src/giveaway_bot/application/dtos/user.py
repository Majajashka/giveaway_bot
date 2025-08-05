from dataclasses import dataclass

from giveaway_bot.entities.enum.language import Language
from giveaway_bot.entities.enum.role import Role


@dataclass
class UserCreateDTO:
    tg_id: int
    username: str | None = None
    language: Language = Language.RU
    role: Role = Role.USER
