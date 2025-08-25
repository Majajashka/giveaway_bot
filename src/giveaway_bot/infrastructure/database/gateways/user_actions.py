from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, select
from giveaway_bot.application.dtos.giveaway import GiveawayStatsDTO
from giveaway_bot.entities.enum.user_action import UserActionEnum
from giveaway_bot.infrastructure.database.models.user_actions import UserActionsORM
from giveaway_bot.application.interfaces.dao.user_action import UserActionsRepository
from sqlalchemy import func, case

class UserActionsRepositoryImpl(UserActionsRepository):

    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(
        self,
        tg_id: int,
        giveaway_id: UUID,
        action: UserActionEnum,
    ) -> None:
        stmt = (
            insert(UserActionsORM)
            .values(
                tg_id=tg_id,
                giveaway_id=giveaway_id,
                action=action.value,
            )
        )
        await self._session.execute(stmt)

    async def exists(
        self,
        tg_id: int,
        giveaway_id: UUID,
        action: UserActionEnum
    ) -> bool:
        stmt = (
            select(UserActionsORM)
            .where(
                UserActionsORM.tg_id == tg_id,
                UserActionsORM.giveaway_id == giveaway_id,
                UserActionsORM.action == action.value,
            )
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None
    
    async def get_stats(self, giveaway_id: UUID) -> GiveawayStatsDTO:
        stmt = (
            select(
                func.count(
                    case(
                        (UserActionsORM.action == UserActionEnum.JOINED_GIVEAWAY.value, UserActionsORM.tg_id.distinct())
                    )
                ).label("participants_count"),
                func.count(
                    case(
                        (UserActionsORM.action == UserActionEnum.SUBSCRIBED_TO_CHANNELS.value, UserActionsORM.tg_id.distinct())
                    )
                ).label("channel_subscriptions_count"),
                func.count(
                    case(
                        (UserActionsORM.action == UserActionEnum.COMPLETED_REGISTRATION.value, UserActionsORM.tg_id.distinct())
                    )
                ).label("registrations_count"),
                func.count(
                    case(
                        (UserActionsORM.action == UserActionEnum.ACTIVATE_GIVEAWAY_SUBSCRIPTION.value, UserActionsORM.tg_id.distinct())
                    )
                ).label("activate_giveaway_subscription_count"),
                func.count(
                    case(
                        (UserActionsORM.action == UserActionEnum.DEACTIVATE_GIVEAWAY_SUBSCRIPTION.value, UserActionsORM.tg_id.distinct())
                    )
                ).label("deactivate_giveaway_subscription_count"),
            )
            .where(UserActionsORM.giveaway_id == giveaway_id)
        )

        result = await self._session.execute(stmt)
        row = result.one()

        return GiveawayStatsDTO(
            participants_count=row.participants_count,
            channel_subscriptions_count=row.channel_subscriptions_count,
            registrations_count=row.registrations_count,
            activate_giveaway_subscription_count=row.activate_giveaway_subscription_count,
            deactivate_giveaway_subscription_count=row.deactivate_giveaway_subscription_count
        )
