from datetime import datetime
from typing import AsyncGenerator
from uuid import UUID

from sqlalchemy import insert, select, func, update
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
            media_id=giveaway_data.media.id,
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

    async def get_all(self, active_only: bool = False) -> list[Giveaway]:
        stmt = select(GiveawayORM)
        if active_only:
            stmt = stmt.where(GiveawayORM.ends_at > func.now())

        result = await self.session.scalars(stmt)
        return [self._orm_to_domain(orm_obj) for orm_obj in result.all()]

    async def edit_giveaway_date(
        self,
        giveaway_id: UUID,
        new_date: datetime
    ) -> None:
        """Edit the end date of a giveaway."""
        stmt = (
            update(GiveawayORM)
            .where(GiveawayORM.id == giveaway_id)
            .values(ends_at=new_date)
            .returning(GiveawayORM)
        )
        data = await self.session.execute(stmt)

    def _orm_to_domain(self, orm: GiveawayORM) -> Giveaway:
        return giveaway_orm_to_giveaway(orm)
