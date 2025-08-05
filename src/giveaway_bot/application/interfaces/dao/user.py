from typing import Protocol

from giveaway_bot.application.dtos.user import UserCreateDTO
from giveaway_bot.entities.domain.user import User


class UserRepository(Protocol):

    async def get_user(self, id_: int) -> User | None:
        raise NotImplementedError

    async def get_user_by_tg_id(self, tg_id: int) -> User | None:
        raise NotImplementedError

    async def create_user(self, data: UserCreateDTO) -> User:
        raise NotImplementedError
