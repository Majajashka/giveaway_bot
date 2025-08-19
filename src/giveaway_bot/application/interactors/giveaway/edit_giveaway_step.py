from typing import Literal
from uuid import UUID

from giveaway_bot.application.dtos.giveaway import GiveawayStepDTO, CreateGiveawayStepDTO
from giveaway_bot.application.interfaces.dao.giveaway import GiveawayRepository
from giveaway_bot.application.interfaces.dao.media import MediaRepository
from giveaway_bot.application.interfaces.uow import UoW
from giveaway_bot.application.services.giveaway import GiveawayService
from giveaway_bot.entities.domain.giveaway import Giveaway
from giveaway_bot.entities.enum.media import MediaType


class EditGiveawayStepInteractor:

    def __init__(self, giveaway_repo: GiveawayRepository, media_repo: MediaRepository, uow: UoW):
        self._giveaway_repo = giveaway_repo
        self.media_repo = media_repo
        self.uow = uow

    async def execute(
            self,
            giveaway_id: UUID,
            step_type: Literal["description", "subscription", "integration", "success"],
            giveaway_step: GiveawayStepDTO,
    ) -> Giveaway:
        """
        Edit a step of a giveaway.

        :param giveaway_id: ID of the giveaway.
        :param step_type: Type of the step to edit (description, subscription, integration, success).
        :param new_text: New text for the step.
        :param media_ids: List of media IDs to associate with the step.
        """
        await self._giveaway_repo.update_step(
            giveaway_id=giveaway_id,
            step_type=step_type,
            step_data=await self._create_step(giveaway_step, step_type, giveaway_id),
        )
        await self.uow.commit()
        giveaway = await self._giveaway_repo.get_by_id(giveaway_id=giveaway_id)
        return giveaway

    async def _create_step(self, step: GiveawayStepDTO, step_type: Literal["description", "subscription", "integration", "success"], giveaway_id: UUID) -> CreateGiveawayStepDTO:
        if step.media:
            media = [
                await self.media_repo.create_media(data=data, media_type=MediaType.PHOTO)
                for data in step.media
            ]
        else:
            if step_type == "description":
                giveaway = await self._giveaway_repo.get_by_id(giveaway_id=giveaway_id)
                media = giveaway.description_step.media
            else:
                media = None

        return CreateGiveawayStepDTO(
            text=step.text,
            media=media
        )
