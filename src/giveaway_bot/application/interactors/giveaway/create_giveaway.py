from dataclasses import dataclass
from datetime import datetime
from io import BytesIO

from giveaway_bot.application.dtos.giveaway import CreateGiveawayDTO, CreateGiveawayStepDTO, GiveawayStepDTO
from giveaway_bot.application.interfaces.dao.giveaway import GiveawayRepository
from giveaway_bot.application.interfaces.dao.media import MediaRepository
from giveaway_bot.application.interfaces.uow import UoW
from giveaway_bot.entities.domain.giveaway import Giveaway
from giveaway_bot.entities.enum.media import MediaType





class CreateGiveawayInteractor:
    def __init__(self, giveaway_repo: GiveawayRepository, media_repo: MediaRepository, uow: UoW):
        self.giveaway_repo = giveaway_repo
        self.media_repo = media_repo
        self.uow = uow

    async def execute(
            self,
            title: str,
            integration_url: str,
            description_step_data: GiveawayStepDTO,
            subscription_step_data: GiveawayStepDTO | None = None,
            integration_step_data: GiveawayStepDTO | None = None,
            success_step_data: GiveawayStepDTO | None = None,
    ) -> Giveaway:
        description_step = await self._create_step(description_step_data)
        subscription_step = await self._create_step(subscription_step_data) if subscription_step_data else None
        integration_step = await self._create_step(integration_step_data) if integration_step_data else None
        success_step = await self._create_step(success_step_data) if success_step_data else None

        giveaway_data = CreateGiveawayDTO(
            title=title,
            integration_url=integration_url,
            hide_integration=False,
            ends_at=datetime.now().replace(year=2050),
            description_step=description_step,
            subscription_step=subscription_step,
            integration_step=integration_step,
            success_step=success_step,
        )
        giveaway = await self.giveaway_repo.create(giveaway_data)
        await self.uow.commit()
        return giveaway

    async def _create_step(self, step: GiveawayStepDTO) -> CreateGiveawayStepDTO:
        if step.media:
            media = [
                await self.media_repo.create_media(data=data, media_type=MediaType.PHOTO)
                for data in step.media
            ]
        else:
            media = None

        return CreateGiveawayStepDTO(
            text=step.text,
            media=media
        )