import logging
from dataclasses import dataclass

from giveaway_bot.application.interfaces.subscription import ChannelLinkService
from giveaway_bot.application.services.subcription import SubscriptionCheckingResult as _SubscriptionCheckingResult, \
    SubscriptionCheckService

logger = logging.getLogger(__name__)


@dataclass
class SubscriptionCheckingResult:
    subscribed_channels: list[str]
    not_subscribed_channels: list[str]

    @property
    def is_fully_subscribed(self) -> bool:
        """True if user is subscribed to all required channels (excluding failed ones)."""
        return not self.not_subscribed_channels and self.subscribed_channels


class CheckSubscriptionInteractor:

    def __init__(self, checker_service: SubscriptionCheckService, link_service: ChannelLinkService):
        self.checker_service = checker_service
        self.link_service = link_service

    async def execute(self, user_id: int) -> SubscriptionCheckingResult:
        result = await self.checker_service.check_subscriptions(user_id=user_id)
        if result.failed_channels:
            logger.error(
                f"Failed to check subscription for channels: {result.failed_channels}"
            )
        if result.is_check_failed:
            for channel in result.failed_channels:
                logger.warning(f"Subscription check failed for channel {channel}")
                try:
                    await self.link_service.get_link(channel)
                except ValueError:
                    pass
        result = SubscriptionCheckingResult(
            subscribed_channels=[await self.link_service.get_link(channel) for channel in result.subscribed_channels],
            not_subscribed_channels=[await self.link_service.get_link(channel) for channel in result.not_subscribed_channels],
        )
        return result
