from uuid import UUID

from giveaway_bot.application.services.giveaway import GiveawayService, GiveawaySteps


class GetGiveawayStepsInteractor:

    def __init__(self, giveaway_service: GiveawayService):
        self._giveaway_service = giveaway_service

    async def execute(self, giveaway_id: UUID, user_id: int) -> GiveawaySteps | None:
        return await self._giveaway_service.get_giveaway_steps(giveaway_id, user_id)
