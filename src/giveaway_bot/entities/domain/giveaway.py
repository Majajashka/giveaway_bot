from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from giveaway_bot.application.dtos.giveaway import GiveawayStatsDTO
from giveaway_bot.entities.domain.media import Media


@dataclass
class GiveawayStep:
    text: str
    media: list[Media] | None = None


@dataclass
class Giveaway:
    id: UUID
    title: str
    ends_at: datetime
    hide_integration: bool
    integration_url: str
    created_at: datetime

    description_step: GiveawayStep
    subscription_step: GiveawayStep | None = None
    integration_step: GiveawayStep | None = None
    success_step: GiveawayStep | None = None

    stats: GiveawayStatsDTO | None = None

    def is_active(self, now: datetime) -> bool:
        return now < self.ends_at

    def days_left(self, now: datetime) -> int:
        delta = self.ends_at - now
        return max(delta.days, 0)

    def hours_left(self, now: datetime) -> int:
        delta = self.ends_at - now
        return (delta.seconds // 3600) if delta.days >= 0 else 0
