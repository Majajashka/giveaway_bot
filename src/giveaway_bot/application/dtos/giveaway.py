from dataclasses import dataclass
from datetime import datetime
from io import BytesIO

from giveaway_bot.entities.domain.media import Media


@dataclass
class CreateGiveawayStepDTO:
    text: str
    media: list[Media] | None = None


@dataclass
class GiveawayStepDTO:
    text: str
    media: list[BytesIO] | None = None


@dataclass
class CreateGiveawayDTO:
    title: str
    ends_at: datetime
    description_step: CreateGiveawayStepDTO
    integration_url: str
    hide_integration: bool
    subscription_step: CreateGiveawayStepDTO | None = None
    integration_step: CreateGiveawayStepDTO | None = None
    success_step: CreateGiveawayStepDTO | None = None
