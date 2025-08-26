from typing import Protocol
from uuid import UUID

from giveaway_bot.application.dtos.giveaway import GiveawayStatsDTO
from giveaway_bot.entities.enum.user_action import UserActionEnum


class UserActionsRepository(Protocol):

    async def create(
        self,
        tg_id: int,
        giveaway_id: UUID,
        action: UserActionEnum,
    ):
        raise NotImplementedError

    async def exists(
        self,
        tg_id: int,
        giveaway_id: UUID,
        action: UserActionEnum
    ) -> bool:
        raise NotImplementedError
    
    async def get_stats(self, giveaway_id: UUID | None = None) -> GiveawayStatsDTO:
        raise NotImplementedError