from giveaway_bot.application.interfaces.dao.user import UserRepository


class GetAllUsersInteractor:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def execute(self):
        users = await self.user_repository.get_all_users()
        return users