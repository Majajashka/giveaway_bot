from uuid import UUID

from giveaway_bot.application.interfaces.dao.giveaway import GiveawayRepository
from giveaway_bot.entities.domain.giveaway import Giveaway


class EditGiveawayDescriptionInteractor:
    def __init__(self, giveaway_repo: GiveawayRepository):
        self.giveaway_repo = giveaway_repo

    async def execute(self, giveaway_id: UUID, description: str) -> Giveaway:
        ...