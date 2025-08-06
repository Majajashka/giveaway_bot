import uuid

from sqlalchemy import UUID
from sqlalchemy.orm import Mapped, mapped_column

from giveaway_bot.infrastructure.database.models.base import Base
from giveaway_bot.infrastructure.database.models.mixins import TimestampMixin


class MediaORM(Base, TimestampMixin):
    __tablename__ = "media"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    path: Mapped[str]
    type: Mapped[str]
