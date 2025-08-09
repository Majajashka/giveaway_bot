import logging

from giveaway_bot.application.interfaces.dao.postback import PostbackRepository
from giveaway_bot.application.interfaces.uow import UoW

logger = logging.getLogger(__name__)


class SavePostbackInteractor:
    def __init__(self, postback_repository: PostbackRepository, uow: UoW):
        self.postback_repository = postback_repository
        self.uow = uow

    async def execute(self, tg_id: int, postback_data: dict) -> None:
        await self.postback_repository.save(tg_id=tg_id, data=postback_data)
        await self.uow.commit()
        logger.info("Postback data saved for tg_id: %s", tg_id)
