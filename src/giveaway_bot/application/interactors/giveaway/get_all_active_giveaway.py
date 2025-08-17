from giveaway_bot.application.interfaces.dao.giveaway import GiveawayRepository
from giveaway_bot.entities.domain.giveaway import Giveaway


class GetAllActiveGiveawayInteractor:
    def __init__(self, giveaway_repo: GiveawayRepository):
        self.giveaway_repo = giveaway_repo

    async def execute(self) -> list[Giveaway]:
        """
        Get all active giveaways.

        :return: List of active giveaways.
        """
        return await self.giveaway_repo.get_all(active_only=False)