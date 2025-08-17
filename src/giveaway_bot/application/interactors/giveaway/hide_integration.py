from uuid import UUID

from giveaway_bot.application.interfaces.dao.giveaway import GiveawayRepository
from giveaway_bot.application.interfaces.uow import UoW
from giveaway_bot.entities.domain.giveaway import Giveaway


class HideIntegrationInteractor:
    def __init__(self, giveaway_repo: GiveawayRepository, uow: UoW):
        self._giveaway_repo = giveaway_repo
        self._uow = uow

    async def execute(self, giveaway_id: UUID) -> Giveaway:
        await self._giveaway_repo.change_giveaway_hide_integration(giveaway_id=giveaway_id)
        await self._uow.commit()
        giveaway = await self._giveaway_repo.get_by_id(giveaway_id=giveaway_id)
        return giveaway
