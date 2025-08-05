from adaptix._internal.conversion.facade.func import get_converter
from adaptix._internal.conversion.facade.provider import link, coercer
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from giveaway_bot.application.dtos.user import UserCreateDTO
from giveaway_bot.application.interfaces.dao.user import UserRepository
from giveaway_bot.entities.domain.user import User
from giveaway_bot.entities.enum.language import Language
from giveaway_bot.entities.enum.role import Role
from giveaway_bot.infrastructure.database.models.user import UserORM

orm_to_user = get_converter(
    UserORM,
    User,
    recipe=[
       coercer(str, Language, lambda x: Language(x.lower())),
       coercer(str, Role, lambda x: Role(x.lower())),
    ]

)


class UserRepositoryImpl(UserRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_user(self, id_: int) -> User | None:
        stmt = (
            select(UserORM)
            .where(UserORM.id == id_)
        )
        data = await self._session.execute(stmt)
        user_orm = data.scalar_one_or_none()
        return self._to_entity(user_orm) if user_orm else None

    async def get_user_by_tg_id(self, tg_id: int) -> User | None:
        stmt = (
            select(UserORM)
            .where(UserORM.tg_id == tg_id)
        )
        data = await self._session.execute(stmt)
        user_orm = data.scalar_one_or_none()
        return self._to_entity(user_orm) if user_orm else None

    async def create_user(self, data: UserCreateDTO) -> User:
        stmt = (
            insert(UserORM)
            .values(
                tg_id=data.tg_id,
                role=data.role,
                username=data.username,
                language=data.language,
            )
            .returning(UserORM)
        )
        result = await self._session.execute(stmt)
        user_orm = result.scalars().one()
        return self._to_entity(user_orm)


    @staticmethod
    def _to_entity(model: UserORM) -> User:
        return orm_to_user(model)
