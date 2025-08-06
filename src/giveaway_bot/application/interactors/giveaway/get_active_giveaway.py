from uuid import UUID

from giveaway_bot.application.interfaces.dao.giveaway import GiveawayRepository
from giveaway_bot.entities.domain.giveaway import Giveaway


class GetActiveGiveawayInteractor:

    def __init__(self, giveaway_repo: GiveawayRepository):
        self.giveaway_repo = giveaway_repo

    async def execute(self, giveaway_id: UUID) -> Giveaway | None:
        """
        Get the active giveaway by its ID.

        :param giveaway_id: The ID of the giveaway to retrieve.
        :return: The active giveaway details as a string.
        """
        giveaway = await self.giveaway_repo.get_by_id(giveaway_id)
        if not giveaway:
            return None

        return giveaway
