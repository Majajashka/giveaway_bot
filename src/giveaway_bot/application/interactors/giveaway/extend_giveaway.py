import datetime
from uuid import UUID

from giveaway_bot.application.interfaces.dao.giveaway import GiveawayRepository
from giveaway_bot.application.interfaces.uow import UoW
from giveaway_bot.entities.domain.giveaway import Giveaway


class ExtendGiveawayInteractor:
    def __init__(self, giveaway_repo: GiveawayRepository, uow: UoW):
        self.giveaway_repo = giveaway_repo
        self.uow = uow

    async def execute(self, giveaway_id: UUID, date: datetime) -> Giveaway:
        """
        Extend the end date of a giveaway.
        :param giveaway_id: The ID of the giveaway to extend.
        :param date: The new end date for the giveaway.
        """
        await self.giveaway_repo.edit_giveaway_date(giveaway_id, date)
        await self.uow.commit()
        giveaway = await self.giveaway_repo.get_by_id(giveaway_id)
        return giveaway