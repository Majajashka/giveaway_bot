from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import mapped_column, Mapped

from giveaway_bot.infrastructure.database.models.base import Base
from giveaway_bot.infrastructure.database.models.mixins import TimestampMixin


class GiveawayPostbackORM(Base, TimestampMixin):
    __tablename__ = "giveaway_postbacks"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tg_id: Mapped[int] = mapped_column(ForeignKey("users.tg_id"))
    data: Mapped[dict] = mapped_column(JSON)
