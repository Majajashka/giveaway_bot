from uuid import UUID

from giveaway_bot.application.interfaces.dao.giveaway import GiveawayRepository
from giveaway_bot.application.interfaces.uow import UoW


class EndGiveawayInteractor:
    def __init__(self, giveaway_repo: GiveawayRepository, uow: UoW):
        self.giveaway_repo = giveaway_repo
        self.uow = uow

    async def execute(self, giveaway_id: UUID) -> None:
        """
        Ends the giveaway with the given ID.
        """
        ...