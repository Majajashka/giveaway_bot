from sqlalchemy.ext.asyncio import AsyncSession

from giveaway_bot.application.interfaces.uow import UoW


class SqlalchemyUoW(UoW):

    def __init__(self, session: AsyncSession):
        self._session = session

    async def commit(self) -> None:
        """Commit the transaction."""
        await self._session.commit()

    async def rollback(self) -> None:
        """Rollback the transaction."""
        await self._session.rollback()

    async def flush(self) -> None:
        """Flush the session."""
        await self._session.flush()
