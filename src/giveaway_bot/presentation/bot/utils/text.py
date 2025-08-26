import logging
from dataclasses import asdict

from aiogram.types import Message

from giveaway_bot.application.dtos.giveaway import GiveawayStatsDTO
from giveaway_bot.entities.domain.giveaway import Giveaway
from giveaway_bot.infrastructure.localization.translator import Localization
from giveaway_bot.presentation.bot.utils.clock import LocalizedClock

logger = logging.getLogger(__name__)

def format_stats_text(stats: GiveawayStatsDTO) -> str:
    stats = []
    logger.info(f"Formatting stats: {stats}")
    stats_dict = asdict(stats)
    field_map = {
        "participants_count": "Участников",
        "channel_subscriptions_count": "Подписок на канал",
        "registrations_count": "Регистраций",
        "activate_giveaway_subscription_count": "Активаций подписки",
        "deactivate_giveaway_subscription_count": "Деактиваций подписки"
    }
    for field, label in field_map.items():
        value = stats_dict.get(field)
        if value is not None:
            stats.append(f"{label}: {value}")

    try:
        activation_rate = stats.activation_rate
        only_subscription_rate = stats.only_subscription_rate
        registration_rate = stats.registration_rate
        stats.append(f"Конверсия в подписку на сервис: {activation_rate:.1f}%")
        stats.append(f"Только подписка на канал (без регистрации): {only_subscription_rate:.1f}%")
        stats.append(f"Конверсия в регистрацию: {registration_rate:.1f}%")
    except Exception as e:
        logger.error(f"Failed to calculate rates: {e}")

    return "\n\n" + "\n".join(stats)

def format_giveaway_text(giveaway: Giveaway, clock: LocalizedClock, i18n: Localization, bot_username: str) -> str:
    ended = giveaway.ends_at <= clock.now()

    if not ended:
        delta = giveaway.ends_at - clock.now()
        days = delta.days
        hours = delta.seconds // 3600
        time_left = f"{days} дн. {hours} ч."
    else:
        time_left = ""

    text = i18n(
        "giveaway-admin-info",
        title=giveaway.title,
        id=str(giveaway.id.hex),
        created_at=clock.convert_utc_to_local(giveaway.created_at),
        time_left=time_left,
        integrated_url=giveaway.integration_url,
        url=f"https://t.me/{bot_username}?start={giveaway.id}"
    )
    blocks = []
    if giveaway.stats:
        stats = []
        stats_dict = asdict(giveaway.stats)
        field_map = {
            "participants_count": "Участников",
            "channel_subscriptions_count": "Подписок на канал",
            "registrations_count": "Регистраций",
            "activate_giveaway_subscription_count": "Активаций подписки",
            "deactivate_giveaway_subscription_count": "Деактиваций подписки"
        }
        for field, label in field_map.items():
            value = stats_dict.get(field)
            if value is not None:
                stats.append(f"{label}: {value}")

        try:
            activation_rate = giveaway.stats.activation_rate
            only_subscription_rate = giveaway.stats.only_subscription_rate
            registration_rate = giveaway.stats.registration_rate
            stats.append(f"Конверсия в подписку на сервис: {activation_rate:.1f}%")
            stats.append(f"Только подписка на канал (без регистрации): {only_subscription_rate:.1f}%")
            stats.append(f"Конверсия в регистрацию: {registration_rate:.1f}%")
        except Exception as e:
            logger.error(f"Failed to calculate rates: {e}")

        if stats:
            blocks.append("\n\n" + "\n".join(stats))

    if giveaway.description_step:
        blocks.append(f"\n\nОписание розыгрыша:\n<blockquote expandable>{giveaway.description_step.text}</blockquote>")
    if giveaway.subscription_step:
        blocks.append(f"\n\nТекст подписки:\n<blockquote expandable>{giveaway.subscription_step.text}</blockquote>")
    if giveaway.integration_step:
        blocks.append(f"\n\nТекст интеграции:\n<blockquote expandable>{giveaway.integration_step.text}</blockquote>")
    if giveaway.success_step:
        blocks.append(f"\n\nТекст успеха:\n<blockquote expandable>{giveaway.success_step.text}</blockquote>")

    final_text = text
    for block in blocks:
        if len(final_text) + len(block) <= 1024:
            final_text += block
        else:
            break  # avoid limit breaking

    return final_text


async def try_delete_message(msg: Message):
    try:
        await msg.delete()
    except Exception as e:
        logger.error(f"Failed to delete message: {e}")
