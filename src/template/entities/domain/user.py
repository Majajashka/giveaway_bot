from dataclasses import dataclass
from datetime import datetime

from template.entities.enum.language import Language
from template.entities.enum.role import Role


@dataclass
class User:
    id: int
    tg_id: int
    username: str | None
    role: Role
    language: Language
    is_banned: bool
    is_active: bool
    created_at: datetime

    def active(self):
        return self.is_active and not self.is_banned

