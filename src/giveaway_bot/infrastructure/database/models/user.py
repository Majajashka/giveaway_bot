from sqlalchemy import BigInteger, false, true
from sqlalchemy.orm import Mapped, mapped_column

from giveaway_bot.entities.enum.language import Language
from giveaway_bot.entities.enum.role import Role
from giveaway_bot.infrastructure.database.models.base import Base
from giveaway_bot.infrastructure.database.models.mixins import TimestampMixin


class UserORM(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True, nullable=False)
    tg_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, unique=True)
    username: Mapped[str | None] = mapped_column(nullable=True)
    language: Mapped[str] = mapped_column(default=Language.RU.value)
    role: Mapped[str] = mapped_column(default=Role.USER.value, nullable=False)
    is_banned: Mapped[bool] = mapped_column(server_default=false())
    is_active: Mapped[bool] = mapped_column(server_default=true())
