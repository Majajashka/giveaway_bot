"""add default settings

Revision ID: ac6529e10c6e
Revises: 2ae3df7f6dce
Create Date: 2025-08-10 19:31:29.328677

"""
import uuid
from datetime import datetime, UTC
from typing import Sequence, Union, Mapping

from alembic import op
import sqlalchemy as sa
from sqlalchemy import MetaData, func, DateTime, Column, Table, UUID, ForeignKey, delete
from sqlalchemy.orm import Session, DeclarativeBase, Mapped, mapped_column, relationship

# revision identifiers, used by Alembic.
revision: str = 'ac6529e10c6e'
down_revision: Union[str, None] = 'e59f241eb36d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

convention: Mapping[str, str] = {
    "ix": "ix__%(column_0_label)s",
    "uq": "uq__%(table_name)s__%(column_0_name)s",
    "ck": "ck__%(table_name)s__%(constraint_name)s",
    "fk": "%(table_name)s_%(column_0_name)s_fkey",
    "pk": "pk__%(table_name)s",
}
meta = MetaData(naming_convention=convention)


class Base(DeclarativeBase):
    metadata = meta


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=func.now(),
        server_default=func.now(),
    )


class SettingsORM(Base, TimestampMixin):
    __tablename__ = "settings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    key: Mapped[str] = mapped_column(unique=True, nullable=False)
    value: Mapped[str] = mapped_column(nullable=False)


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


class MediaORM(Base, TimestampMixin):
    __tablename__ = "media"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    path: Mapped[str]
    type: Mapped[str]


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


def upgrade() -> None:
    session = Session(bind=op.get_bind())
    default_dialog = GiveawayORM(
        id=uuid.uuid4(),
        title="DEFAULT",
        ends_at=datetime(2020, 12, 31, 23, 59, 59),
        description="Описание розыгрыша",
        subscription_text="Подписка",
        integration_text="Зарегестрируйтесь по ссылке! <url>",
        success_text="Успех!",
        integration_link="https://example.com/giveaway",
    )
    session.add(default_dialog)
    session.commit()


def downgrade() -> None:
    session = Session(bind=op.get_bind())
    stmt = delete(GiveawayORM).where(GiveawayORM.title == "DEFAULT")
    session.execute(stmt)
    session.commit()
