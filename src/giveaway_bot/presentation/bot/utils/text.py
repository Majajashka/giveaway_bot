from giveaway_bot.entities.domain.giveaway import Giveaway
from giveaway_bot.infrastructure.localization.translator import Localization
from giveaway_bot.presentation.bot.utils.clock import LocalizedClock


def format_giveaway_text(giveaway: Giveaway, clock: LocalizedClock, i18n: Localization, bot_username: str) -> str:
    ended = giveaway.ends_at <= clock.now()

    text = i18n(
        "giveaway-admin-info",
        title=giveaway.title,
        id=str(giveaway.id.hex),
        created_at=clock.convert_utc_to_local(giveaway.created_at),
        integrated_url=giveaway.integration_url,

        url=f"https://t.me/{bot_username}?start={giveaway.id}",
    )
    return text
