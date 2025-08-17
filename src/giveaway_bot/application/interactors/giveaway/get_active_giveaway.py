from uuid import UUID

from giveaway_bot.application.interfaces.clock import Clock
from giveaway_bot.application.interfaces.dao.giveaway import GiveawayRepository
from giveaway_bot.entities.domain.giveaway import Giveaway


class GetActiveGiveawayInteractor:

    def __init__(self, giveaway_repo: GiveawayRepository, clock: Clock):
        self.giveaway_repo = giveaway_repo
        self.clock = clock

    async def execute(self, giveaway_id: UUID) -> Giveaway | None:
        giveaway = await self.giveaway_repo.get_by_id(giveaway_id)
        # if not giveaway or not giveaway.is_active(now=self.clock.now()):
        #     return None

        return giveaway
