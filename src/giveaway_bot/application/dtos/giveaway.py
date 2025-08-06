from dataclasses import dataclass
from datetime import datetime

from giveaway_bot.entities.domain.media import Media


@dataclass
class CreateGiveawayDTO:
    title: str
    description: str
    media: Media
    ends_at: datetime
