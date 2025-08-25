from adaptix._internal.conversion.facade.func import get_converter
from adaptix._internal.conversion.facade.provider import coercer

from giveaway_bot.application.dtos.giveaway import GiveawayStatsDTO
from giveaway_bot.entities.domain.giveaway import Giveaway, GiveawayStep
from giveaway_bot.entities.domain.media import Media
from giveaway_bot.entities.enum.media import MediaType
from giveaway_bot.infrastructure.database.models import GiveawayORM, MediaORM

media_orm_to_media = get_converter(
    MediaORM,
    Media,
    recipe=[
        coercer(str, MediaType, lambda x: MediaType(x)),
    ]
)


def giveaway_orm_to_giveaway(giveaway: GiveawayORM, stats: GiveawayStatsDTO | None = None) -> Giveaway:
    return Giveaway(
        id=giveaway.id,
        title=giveaway.title,
        ends_at=giveaway.ends_at,
        created_at=giveaway.created_at,
        description_step=GiveawayStep(
            text=giveaway.description,
            media=[media_orm_to_media(media) for media in giveaway.media] if giveaway.media else None
        ) if giveaway.description is not None else None,
        subscription_step=GiveawayStep(
            text=giveaway.subscription_text,
            media=[media_orm_to_media(media) for media in
                   giveaway.subscription_media] if giveaway.subscription_media else None
        ) if giveaway.subscription_text is not None else None,
        integration_step=GiveawayStep(
            text=giveaway.integration_text,
            media=[media_orm_to_media(media) for media in
                   giveaway.integration_media] if giveaway.integration_media else None
        ) if giveaway.integration_text is not None else None,
        success_step=GiveawayStep(
            text=giveaway.success_text,
            media=[media_orm_to_media(media) for media in giveaway.success_media] if giveaway.success_media else None
        ) if giveaway.success_text is not None else None,
        hide_integration=giveaway.hide_integration,
        integration_url=giveaway.integration_url,
        stats=stats
    )
