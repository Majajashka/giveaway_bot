from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from giveaway_bot.entities.enum.media import MediaType


@dataclass
class Media:
    id: UUID
    path: str
    type: MediaType
    created_at: datetime

    @property
    def filename(self) -> str:
        return f"{self.id}.{self.type.extension}"
