from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from giveaway_bot.infrastructure.database.models import SettingsORM


class SettingsRepo:

    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_hide_integration(self) -> bool:
        stmt = (
            select(SettingsORM.value)
            .where(SettingsORM.key == "hide_integration")
        )
        data = await self._session.execute(stmt)
        result = data.scalars().first()
        if result.casefold() == "true":
            return True
        return False

    async def set_hide_integration(self, value: bool) -> None:
        stmt = (
            update(SettingsORM)
            .where(SettingsORM.key == "hide_integration")
            .values(value=str(value))
        )
        data = await self._session.execute(stmt)
        await self._session.commit()
