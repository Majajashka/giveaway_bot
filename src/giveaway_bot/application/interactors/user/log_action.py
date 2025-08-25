import logging
from uuid import UUID
from giveaway_bot.application.interfaces.dao.user_action import UserActionsRepository
from giveaway_bot.application.interfaces.uow import UoW
from giveaway_bot.entities.enum.user_action import UserActionEnum

logger = logging.getLogger(__name__)

class SaveUserActionInteractor:

    def __init__(self, user_action_repo: UserActionsRepository, uow: UoW):
        self._user_action_repo = user_action_repo
        self._uow = uow

    async def execute(
            self,
            tg_id: int,
            giveaway_id: UUID,
            action: UserActionEnum
    ):
        action_exists = await self._user_action_repo.exists(
            tg_id=tg_id,
            giveaway_id=giveaway_id,
            action=action
        )
        if not action_exists:
            logger.info(f"Logging action {action} for user {tg_id} in giveaway {giveaway_id}")
            await self._user_action_repo.create(
                tg_id=tg_id,
                giveaway_id=giveaway_id,
                action=action
            )
            await self._uow.commit()