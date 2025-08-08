from adaptix._internal.conversion.facade.func import get_converter
from adaptix._internal.conversion.facade.provider import coercer

from giveaway_bot.entities.domain.giveaway import Giveaway
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

giveaway_orm_to_giveaway = get_converter(
    GiveawayORM,
    Giveaway,
    recipe=[
        coercer(str, MediaType, lambda x: MediaType(x)),
    ]
)
