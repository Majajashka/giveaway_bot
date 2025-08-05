import logging

from giveaway_bot.application.dtos.user import UserCreateDTO
from giveaway_bot.application.interfaces.dao.user import UserRepository
from giveaway_bot.application.interfaces.uow import UoW
from giveaway_bot.entities.domain import User

logger = logging.getLogger(__name__)


class GetOrCreateUserInteractor:
    """
    Interactor for getting or creating a user.
    """

    def __init__(self, user_repository: UserRepository, uow: UoW):
        self.user_repository = user_repository
        self._uow = uow

    async def execute(self, data: UserCreateDTO) -> User:
        """
        Get or create a user by ID.

        :param data: The user data.
        :return: The user object.
        """

        user = await self.user_repository.get_user_by_tg_id(data.tg_id)
        if user:
            return user

        user = await self.user_repository.create_user(data)
        await self._uow.commit()
        return user
