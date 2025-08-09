from uuid import UUID

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


class ParticipateGiveawayCallbackData(CallbackData, prefix="giveaway"):
    giveaway_id: UUID


class CheckSubscriptionCallbackData(CallbackData, prefix="check_subscription"):
    giveaway_id: UUID


def get_giveaway_kb(giveaway_id: UUID) -> InlineKeyboardMarkup:
    """
    Get the keyboard for broadcasting a giveaway.

    :param giveaway_id: The ID of the giveaway.
    :return: A dictionary representing the keyboard layout.
    """
    kb = [
        [
            InlineKeyboardButton(
                text="Участвовать",
                callback_data=ParticipateGiveawayCallbackData(
                    giveaway_id=giveaway_id,
                ).pack()
            )
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)


def get_giveaway_broadcast_kb(giveaway_id: UUID, bot_username: str) -> InlineKeyboardMarkup:
    kb = [
        [
            InlineKeyboardButton(text="Участвовать", url=f"https://t.me/{bot_username}?start={giveaway_id}")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)


def build_links_keyboard(
        links: list[str],
        giveaway_id: UUID,
        buttons_per_row: int
) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()

    buttons = [
        InlineKeyboardButton(text=f"Канал {i + 1}", url=link)
        for i, link in enumerate(links)
    ]

    check_subscription = InlineKeyboardButton(
        text="Проверить",
        callback_data=CheckSubscriptionCallbackData(giveaway_id=giveaway_id).pack()
    )

    keyboard.row(*buttons, width=buttons_per_row)
    keyboard.row(check_subscription)
    return keyboard.as_markup()
