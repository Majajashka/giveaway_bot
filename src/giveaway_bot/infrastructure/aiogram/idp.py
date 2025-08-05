
from aiogram.types import User as TGUser

from giveaway_bot.application.interfaces.dao.user import UserRepository
from giveaway_bot.application.interfaces.provider import IdentityProvider
from giveaway_bot.entities.domain.user import User
from giveaway_bot.entities.enum.role import Role


class TGUserIdentityProvider(IdentityProvider):

    def __init__(self, user: TGUser, user_repo: UserRepository):
        self._tg_user = user
        self._user_repo = user_repo
        self._user: User | None = None

    def get_user_id(self) -> int:
        return self._tg_user.id


    async def get_user(self) -> User:
        return await self._get_user()

    async def _get_user(self) -> User:
        if self._user:
            return self._user
        user = await self._user_repo.get_user_by_tg_id(tg_id=self._tg_user.id)
        self._user = user
        return user
