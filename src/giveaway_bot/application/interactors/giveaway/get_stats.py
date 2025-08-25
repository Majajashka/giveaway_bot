from giveaway_bot.application.dtos.giveaway import GiveawayStatsDTO
from giveaway_bot.application.interfaces.dao.user_action import UserActionsRepository


class GetGiveawayStartInteractor:

    def __init__(self, repo: UserActionsRepository):
        self._repo = repo

    async def execute(self, giveaway_id) -> GiveawayStatsDTO:
        return await self._repo.get_stats(giveaway_id)