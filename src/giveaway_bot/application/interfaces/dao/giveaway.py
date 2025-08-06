from typing import Protocol
from uuid import UUID

from giveaway_bot.application.dtos.giveaway import CreateGiveawayDTO
from giveaway_bot.entities.domain.giveaway import Giveaway


class GiveawayRepository(Protocol):

    async def create(self, giveaway_data: CreateGiveawayDTO) -> Giveaway:
        """Create a new giveaway."""
        raise NotImplementedError

    async def get_by_id(self, giveaway_id: UUID) -> Giveaway | None:
        """Get a giveaway by its ID."""
        raise NotImplementedError


