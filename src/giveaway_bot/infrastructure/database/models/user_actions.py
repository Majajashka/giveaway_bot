from uuid import UUID
from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapped_column, Mapped

from giveaway_bot.infrastructure.database.models.base import Base
from giveaway_bot.infrastructure.database.models.mixins import TimestampMixin


class UserActionsORM(Base, TimestampMixin):
    __tablename__ = "user_actions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tg_id: Mapped[int] = mapped_column(ForeignKey("users.tg_id"))
    giveaway_id: Mapped[UUID] = mapped_column(ForeignKey("giveaways.id")) 
    action: Mapped[str]


    
