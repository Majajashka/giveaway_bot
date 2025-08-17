from uuid import UUID

from giveaway_bot.application.interfaces.dao.giveaway import GiveawayRepository
from giveaway_bot.application.interfaces.uow import UoW
from giveaway_bot.entities.domain.giveaway import Giveaway


class EditGiveawayIntegrationUrlInteractor:
    def __init__(self, giveaway_repo: GiveawayRepository, uow: UoW):
        self.uow = uow
        self.giveaway_repo = giveaway_repo

    async def execute(self, giveaway_id: UUID, url: str) -> Giveaway:
        await self.giveaway_repo.edit_integration_url(giveaway_id, url)
        await self.uow.commit()
        giveaway = await self.giveaway_repo.get_by_id(giveaway_id=giveaway_id)
        return giveaway
