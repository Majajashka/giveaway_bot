from io import BytesIO
from uuid import UUID

from giveaway_bot.entities.domain.media import Media
from giveaway_bot.entities.enum.media import MediaType


class MediaRepository:

    async def create_media(self, data: BytesIO, media_type: MediaType) -> Media:
        """Create a new media entry."""
        raise NotImplementedError

    async def get_media_by_id(self, media_id: UUID) -> Media | None:
        """Get media by its ID."""
        raise NotImplementedError

    async def get_media_by_filename(self, filename: str) -> Media | None:
        """Get media by its filename."""
        raise NotImplementedError

    async def delete_media(self, media_id: str) -> None:
        """Delete media by its ID."""
        raise NotImplementedError
