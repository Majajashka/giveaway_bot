import uuid
from datetime import datetime

from sqlalchemy import UUID, DateTime, ForeignKey, Table, Column, false
from sqlalchemy.orm import Mapped, mapped_column, relationship

from giveaway_bot.infrastructure.database.models.base import Base
from giveaway_bot.infrastructure.database.models.media import MediaORM
from giveaway_bot.infrastructure.database.models.mixins import TimestampMixin

giveaway_main_media = Table(
    "giveaway_main_media",
    Base.metadata,
    Column("giveaway_id", UUID(as_uuid=True), ForeignKey("giveaways.id"), primary_key=True),
    Column("media_id", UUID(as_uuid=True), ForeignKey("media.id"), primary_key=True),
)

giveaway_subscription_media = Table(
    "giveaway_subscription_media",
    Base.metadata,
    Column("giveaway_id", UUID(as_uuid=True), ForeignKey("giveaways.id"), primary_key=True),
    Column("media_id", UUID(as_uuid=True), ForeignKey("media.id"), primary_key=True),
)

giveaway_integration_media = Table(
    "giveaway_integration_media",
    Base.metadata,
    Column("giveaway_id", UUID(as_uuid=True), ForeignKey("giveaways.id"), primary_key=True),
    Column("media_id", UUID(as_uuid=True), ForeignKey("media.id"), primary_key=True),
)

giveaway_success_media = Table(
    "giveaway_success_media",
    Base.metadata,
    Column("giveaway_id", UUID(as_uuid=True), ForeignKey("giveaways.id"), primary_key=True),
    Column("media_id", UUID(as_uuid=True), ForeignKey("media.id"), primary_key=True),
)


class GiveawayORM(Base, TimestampMixin):
    __tablename__ = "giveaways"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str]
    ends_at: Mapped[datetime] = mapped_column(DateTime(), nullable=False)
    integration_url: Mapped[str]
    hide_integration: Mapped[bool] = mapped_column(server_default=false())

    description: Mapped[str]
    subscription_text: Mapped[str | None]
    integration_text: Mapped[str | None]
    success_text: Mapped[str | None]

    media: Mapped[list[MediaORM]] = relationship(
        "MediaORM",
        secondary=giveaway_main_media,
        lazy="selectin",
        cascade="all",
    )

    subscription_media: Mapped[list[MediaORM]] = relationship(
        "MediaORM",
        secondary=giveaway_subscription_media,
        lazy="selectin",
        cascade="all",
    )

    integration_media: Mapped[list[MediaORM]] = relationship(
        "MediaORM",
        secondary=giveaway_integration_media,
        lazy="selectin",
        cascade="all",
    )

    success_media: Mapped[list[MediaORM]] = relationship(
        "MediaORM",
        secondary=giveaway_success_media,
        lazy="selectin",
        cascade="all",
    )
