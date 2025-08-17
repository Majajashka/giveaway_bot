from sqlalchemy.orm import Mapped
from sqlalchemy.testing.schema import mapped_column

from giveaway_bot.infrastructure.database.models.base import Base
from giveaway_bot.infrastructure.database.models.mixins import TimestampMixin


class SettingsORM(Base, TimestampMixin):
    __tablename__ = "settings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    key: Mapped[str] = mapped_column(unique=True, nullable=False)
    value: Mapped[str] = mapped_column(nullable=False)
