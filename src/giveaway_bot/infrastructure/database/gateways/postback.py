from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from giveaway_bot.application.interfaces.dao.postback import PostbackRepository
from giveaway_bot.infrastructure.database.models.postback import GiveawayPostbackORM


class PostbackRepoImpl(PostbackRepository):

    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, tg_id: int, data: dict) -> None:
        stmt = (
            insert(GiveawayPostbackORM)
            .values(tg_id=tg_id, data=data)
        )
        result = await self.session.execute(stmt)
