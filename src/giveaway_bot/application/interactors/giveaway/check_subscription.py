import logging

from giveaway_bot.application.services.subcription import SubscriptionCheckingResult, SubscriptionCheckService

logger = logging.getLogger(__name__)


class CheckSubscriptionInteractor:

    def __init__(self, checker_service: SubscriptionCheckService):
        self.checker_service = checker_service

    async def execute(self, user_id: int) -> SubscriptionCheckingResult:
        result = await self.checker_service.check_subscriptions(user_id=user_id)
        if result.failed_channels:
            logger.error(
                f"Failed to check subscription for channels: {result.failed_channels}"
            )
        return result
