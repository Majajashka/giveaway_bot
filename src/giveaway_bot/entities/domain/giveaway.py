from dataclasses import dataclass
from datetime import datetime

from giveaway_bot.entities.domain.media import Media


@dataclass
class Giveaway:
    id: int
    title: str
    media: Media
    ends_at: datetime
    created_at: datetime

    description: str | None = None

    def is_active(self, now: datetime) -> bool:
        return now < self.ends_at

    def days_left(self, now: datetime) -> int:
        delta = self.ends_at - now
        return max(delta.days, 0)

    def hours_left(self, now: datetime) -> int:
        delta = self.ends_at - now
        return (delta.seconds // 3600) if delta.days >= 0 else 0
