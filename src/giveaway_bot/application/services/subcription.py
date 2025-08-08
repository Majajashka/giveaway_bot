import logging
from dataclasses import dataclass

from giveaway_bot.application.exceptions.subscription import BotNotInChannelError
from giveaway_bot.application.interfaces.subscription import SubscriptionChecker

logger = logging.getLogger(__name__)


@dataclass
class SubscriptionCheckingResult:
    subscribed_channels: list[int]
    not_subscribed_channels: list[int]
    failed_channels: list[int]

    @property
    def is_fully_subscribed(self) -> bool:
        """True if user is subscribed to all required channels (excluding failed ones)."""
        return not self.not_subscribed_channels and not self.failed_channels

    @property
    def is_check_failed(self) -> bool:
        """True if some channels could not be verified."""
        return bool(self.failed_channels)


class SubscriptionCheckService:
    """
    Service to check if a user has an active subscription.
    """

    def __init__(self, checker: SubscriptionChecker, required_channels: list[int]):
        self.checker = checker
        self.required_channels = required_channels

    async def check_subscriptions(self, user_id: int) -> SubscriptionCheckingResult:
        subscribed_channels: list[int] = []
        not_subscribed_channels: list[int] = []
        failed_channels: list[int] = []

        for channel in self.required_channels:
            try:
                result = await self.checker.is_subscribed(user_id, channel)
                if result is True:
                    subscribed_channels.append(channel)
                else:
                    not_subscribed_channels.append(channel)
            except BotNotInChannelError:
                failed_channels.append(channel)
            except Exception as e:
                failed_channels.append(channel)
                logger.warning(f"Error checking subscription for channel {channel}: {e}")

        return SubscriptionCheckingResult(
            subscribed_channels=subscribed_channels,
            not_subscribed_channels=not_subscribed_channels,
            failed_channels=failed_channels
        )
