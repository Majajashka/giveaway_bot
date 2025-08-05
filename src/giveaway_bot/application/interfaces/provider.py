from typing import Protocol

from giveaway_bot.entities.domain.user import User
from giveaway_bot.entities.enum.role import Role


class Provider[ObjT](Protocol):
    def get(self) -> ObjT:
        """Retrieve an object from the provider."""
        raise NotImplementedError


class IdentityProvider(Protocol):

    def get_user_id(self) -> int:
        """Retrieve an identity from the provider."""
        raise NotImplementedError

    async def get_user_roles(self) -> set[Role]:
        """Retrieve an identity from the provider."""
        raise NotImplementedError

    async def get_user(self) -> User:
        """Retrieve an identity from the provider."""
        raise NotImplementedError
