from adaptix._internal.conversion.facade.func import get_converter
from adaptix._internal.conversion.facade.provider import coercer

from giveaway_bot.entities.domain.media import Media
from giveaway_bot.entities.enum.media import MediaType
from giveaway_bot.infrastructure.database.models import MediaORM

media_orm_to_media = get_converter(
    MediaORM,
    Media,
    recipe=[
        coercer(str, MediaType, lambda x: MediaType(x)),
    ]
)