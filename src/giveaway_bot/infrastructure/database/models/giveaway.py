import uuid
from datetime import datetime

from sqlalchemy import UUID, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from giveaway_bot.infrastructure.database.models.base import Base
from giveaway_bot.infrastructure.database.models.media import MediaORM
from giveaway_bot.infrastructure.database.models.mixins import TimestampMixin


class GiveawayORM(Base, TimestampMixin):
    __tablename__ = "giveaways"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str]
    description: Mapped[str]
    ends_at: Mapped[datetime] = mapped_column(DateTime(), nullable=False)
    media_id: Mapped[uuid.UUID] = mapped_column(ForeignKey(MediaORM.id), nullable=False)

    media: Mapped[MediaORM] = relationship(
        MediaORM,
        lazy="selectin",
    )

