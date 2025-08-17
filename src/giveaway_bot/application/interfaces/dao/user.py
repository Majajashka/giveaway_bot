from typing import Protocol, AsyncGenerator

from giveaway_bot.application.dtos.user import UserCreateDTO
from giveaway_bot.entities.domain.user import User


class UserRepository(Protocol):

    async def get_user(self, id_: int) -> User | None:
        raise NotImplementedError

    async def get_user_by_tg_id(self, tg_id: int) -> User | None:
        raise NotImplementedError

    async def create_user(self, data: UserCreateDTO) -> User:
        raise NotImplementedError

    async def get_all(self, batch_size: int, are_subscribed: bool | None = None) -> AsyncGenerator[list[User], None]:
        raise NotImplementedError

    async def activate_subscription(self, tg_id: int) -> None:
        raise NotImplementedError

    async def deactivate_subscription(self, tg_id: int) -> None:
        raise NotImplementedError
