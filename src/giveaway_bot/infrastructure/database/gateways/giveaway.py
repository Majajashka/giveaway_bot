from datetime import datetime
from typing import AsyncGenerator, Literal
from uuid import UUID

from sqlalchemy import insert, select, func, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from giveaway_bot.application.dtos.giveaway import CreateGiveawayDTO, CreateGiveawayStepDTO, GiveawayStatsDTO
from giveaway_bot.application.interfaces.dao.giveaway import GiveawayRepository
from giveaway_bot.application.interfaces.dao.user_action import UserActionsRepository
from giveaway_bot.entities.domain.giveaway import Giveaway, GiveawayStep
from giveaway_bot.infrastructure.database.gateways.mapper import giveaway_orm_to_giveaway
from giveaway_bot.infrastructure.database.models import GiveawayORM
from giveaway_bot.infrastructure.database.models.giveaway import giveaway_main_media, giveaway_subscription_media, \
    giveaway_integration_media, giveaway_success_media


class GiveawayRepoImpl(GiveawayRepository):
    def __init__(self, session: AsyncSession, repo: UserActionsRepository):
        self.session = session
        self._repo = repo

    async def create(self, giveaway_data: CreateGiveawayDTO) -> Giveaway:
        giveaway = GiveawayORM(
            title=giveaway_data.title,
            ends_at=giveaway_data.ends_at,
            description=giveaway_data.description_step.text,
            subscription_text=giveaway_data.subscription_step.text if giveaway_data.subscription_step else None,
            integration_text=giveaway_data.integration_step.text if giveaway_data.integration_step else None,
            success_text=giveaway_data.success_step.text if giveaway_data.success_step else None,
            integration_url=giveaway_data.integration_url,
            hide_integration=giveaway_data.hide_integration
        )
        self.session.add(giveaway)
        await self.session.flush()

        async def insert_links(table, media_list):
            if not media_list:
                return
            await self.session.execute(
                insert(table).values([
                    {"giveaway_id": giveaway.id, "media_id": m.id} for m in media_list
                ])
            )

        await insert_links(giveaway_main_media, giveaway_data.description_step.media)
        if giveaway_data.subscription_step:
            await insert_links(giveaway_subscription_media, giveaway_data.subscription_step.media)
        if giveaway_data.integration_step:
            await insert_links(giveaway_integration_media, giveaway_data.integration_step.media)
        if giveaway_data.success_step:
            await insert_links(giveaway_success_media, giveaway_data.success_step.media)

        await self.session.commit()
        await self.session.refresh(giveaway)

        return self._orm_to_domain(giveaway)

    async def update_step(
            self,
            giveaway_id: UUID,
            step_type: Literal["description", "subscription", "integration", "success"],
            step_data: CreateGiveawayStepDTO,
    ):
        field_map = {
            "description": "description",
            "subscription": "subscription_text",
            "integration": "integration_text",
            "success": "success_text",
        }
        if step_type not in field_map:
            raise ValueError(f"Unknown step_type: {step_type}")

        await self.session.execute(
            update(GiveawayORM)
            .where(GiveawayORM.id == giveaway_id)
            .values({field_map[step_type]: step_data.text})
        )

        media_table_map = {
            "description": giveaway_main_media,
            "subscription": giveaway_subscription_media,
            "integration": giveaway_integration_media,
            "success": giveaway_success_media,
        }
        await self.session.execute(
            delete(media_table_map[step_type])
            .where(media_table_map[step_type].c.giveaway_id == giveaway_id)
        )

        if step_data.media:
            await self.session.execute(
                insert(media_table_map[step_type]).values([
                    {"giveaway_id": giveaway_id, "media_id": m.id}
                    for m in step_data.media
                ])
            )


    async def get_by_id(self, giveaway_id: UUID) -> Giveaway | None:
        """Get a giveaway by its ID."""
        stmt = select(GiveawayORM).where(GiveawayORM.id == giveaway_id)
        stats = await self._repo.get_stats(giveaway_id)
        data = await self.session.execute(stmt)
        giveaway_orm = data.scalar_one_or_none()
        return self._orm_to_domain(giveaway_orm, stats) if giveaway_orm else None

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

    async def get_default_dialog(self) -> Giveaway:
        """Get the default dialog for giveaways."""
        stmt = select(GiveawayORM).where(GiveawayORM.title == "DEFAULT")
        data = await self.session.execute(stmt)
        giveaway_orm = data.scalar_one()
        return self._orm_to_domain(giveaway_orm)

    async def change_giveaway_hide_integration(self, giveaway_id: UUID) -> None:
        await self.session.execute(
            update(GiveawayORM)
            .where(GiveawayORM.id == giveaway_id)
            .values(hide_integration=~GiveawayORM.hide_integration)
        )

    async def edit_integration_url(self, giveaway_id: UUID, url: str) -> None:
        await self.session.execute(
            update(GiveawayORM)
            .where(GiveawayORM.id == giveaway_id)
            .values(integration_url=url)
        )

    def _orm_to_domain(self, orm: GiveawayORM, stats: GiveawayStatsDTO | None = None) -> Giveaway:
        return giveaway_orm_to_giveaway(orm, stats)
