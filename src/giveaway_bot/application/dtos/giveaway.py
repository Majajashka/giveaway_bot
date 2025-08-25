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


@dataclass
class GiveawayStatsDTO:
    participants_count: int
    channel_subscriptions_count: int
    registrations_count: int
    activate_giveaway_subscription_count: int
    deactivate_giveaway_subscription_count: int

    @property
    def activation_rate(self) -> float:
        if self.participants_count == 0:
            return 0.0
        return (self.activate_giveaway_subscription_count / self.participants_count) * 100

    @property
    def only_subscription_rate(self) -> float:
        if self.participants_count == 0:
            return 0.0
        return ((self.channel_subscriptions_count - self.registrations_count) / self.participants_count) * 100

    @property
    def registration_rate(self) -> float:
        if self.participants_count == 0:
            return 0.0
        return (self.registrations_count / self.participants_count) * 100

    

