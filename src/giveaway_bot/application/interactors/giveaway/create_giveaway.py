from datetime import datetime
from io import BytesIO

from giveaway_bot.application.dtos.giveaway import CreateGiveawayDTO
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

    async def execute(self, title: str, description: str, media_data: BytesIO, ends_at: datetime) -> Giveaway:
        media = await self.media_repo.create_media(data=media_data, media_type=MediaType.PHOTO)
        giveaway_data = CreateGiveawayDTO(
            title=title,
            description=description,
            media=media,
            ends_at=ends_at
        )
        giveaway = await self.giveaway_repo.create(giveaway_data)
        await self.uow.commit()
        return giveaway

