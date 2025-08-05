from copy import deepcopy

from giveaway_bot.entities.domain import User
from giveaway_bot.entities.enum.role import Role


class AdminPolicy:

    def __init__(self):
        self._permissions = {
            "ban": {Role.ADMIN, Role.SUPERADMIN},
            "broadcast": {Role.ADMIN, Role.SUPERADMIN},
        }

    def can_ban(self, user: User, target: User) -> bool:
        return (
                user.role in self._permissions["ban"]
                and target.role > user.role
        )

    def can_unban(self, user: User, target: User) -> bool:
        return self.can_ban(user, target)

    def can_broadcast(self, user: User) -> bool:
        return user.role in self._permissions["ban"]

    @property
    def permissions(self) -> dict:
        return deepcopy(self._permissions)


a = AdminPolicy()
