import logging

from giveaway_bot.application.interfaces.dao.user import UserRepository
from giveaway_bot.application.interfaces.uow import UoW

logger = logging.getLogger(__name__)


class EditSubscriptionInteractor:

    def __init__(self, user_repo: UserRepository, uow: UoW):
        self.user_repo = user_repo
        self.uow = uow

    async def execute(self, tg_id: int, is_subscribed: bool) -> None:
        if is_subscribed is True:
            logger.info("Activating subscription for tg_id: %s", tg_id)
            await self.user_repo.activate_subscription(tg_id)
        else:
            logger.info("Deactivating subscription for tg_id: %s", tg_id)
            await self.user_repo.deactivate_subscription(tg_id)

        await self.uow.commit()
