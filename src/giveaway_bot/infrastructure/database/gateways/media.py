import uuid
from io import BytesIO

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from giveaway_bot.application.interfaces.dao.media import MediaRepository
from giveaway_bot.entities.domain.media import Media
from giveaway_bot.entities.enum.media import MediaType
from giveaway_bot.infrastructure.database.gateways.mapper import media_orm_to_media
from giveaway_bot.infrastructure.database.models import MediaORM
from giveaway_bot.infrastructure.media_storage import MediaStorage


class MediaRepositoryImpl(MediaRepository):

    def __init__(self, session: AsyncSession, media_storage: MediaStorage):
        self._session = session
        self._media_storage = media_storage

    async def create_media(self, data: BytesIO, media_type: MediaType) -> Media:
        """
        Create a new media record in the database.

        :param data: The media file data.
        :param media_type: The type of the media.
        :return: The created Media object.
        """
        media_uuid = uuid.uuid4()
        data.seek(0)
        media_bytes = data.read()
        filename = f"{media_uuid}.{media_type.extension}"
        await self._media_storage.save_media(media_data=media_bytes, filename=filename)
        media_orm = MediaORM(
            id=media_uuid,
            path=filename,
            type=media_type.value,
        )
        self._session.add(media_orm)
        media_domen = media_orm_to_media(media_orm)
        return media_domen

    async def get_media_by_id(self, media_id: uuid.UUID) -> Media | None:
        stmt = select(MediaORM).where(MediaORM.id == media_id)
        data = await self._session.execute(stmt)
        media_orm = data.scalar_one_or_none()
        return self._orm_to_domain(media_orm) if media_orm else None

    async def get_media_by_filename(self, filename: str) -> Media | None:
        stmt = select(MediaORM).where(MediaORM.path == filename)
        data = await self._session.execute(stmt)
        media_orm = data.scalar_one_or_none()
        return self._orm_to_domain(media_orm) if media_orm else None

    def _orm_to_domain(self, orm: MediaORM) -> Media:
        return media_orm_to_media(orm)
