from uuid import UUID

from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from giveaway_bot.application.dtos.giveaway import CreateGiveawayDTO
from giveaway_bot.application.interfaces.dao.giveaway import GiveawayRepository
from giveaway_bot.entities.domain.giveaway import Giveaway
from giveaway_bot.infrastructure.database.gateways.mapper import giveaway_orm_to_giveaway
from giveaway_bot.infrastructure.database.models import GiveawayORM


class GiveawayRepoImpl(GiveawayRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, giveaway_data: CreateGiveawayDTO) -> Giveaway:
        """Create a new giveaway."""
        giveaway = insert(GiveawayORM).values(
            title=giveaway_data.title,
            description=giveaway_data.description,
            media=giveaway_data.media,
            ends_at=giveaway_data.ends_at
        ).returning(GiveawayORM)
        data = await self.session.execute(giveaway)
        result = data.scalar_one()
        return self._orm_to_domain(result)

    async def get_by_id(self, giveaway_id: UUID) -> Giveaway | None:
        """Get a giveaway by its ID."""
        stmt = select(GiveawayORM).where(GiveawayORM.id == giveaway_id)
        data = await self.session.execute(stmt)
        giveaway_orm = data.scalar_one_or_none()
        return self._orm_to_domain(giveaway_orm) if giveaway_orm else None

    def _orm_to_domain(self, orm: GiveawayORM) -> Giveaway:
        return giveaway_orm_to_giveaway(orm)
