from uuid import UUID

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from giveaway_bot.entities.domain.giveaway import Giveaway


class GiveawayInfoCallbackData(CallbackData, prefix="giveaway_info"):
    giveaway_id: UUID


class ExtendGiveawayCallbackData(CallbackData, prefix="extend_giveaway"):
    giveaway_id: UUID


class ChangeGiveawayDescriptionCallbackData(CallbackData, prefix="change_giveaway_desc"):
    giveaway_id: UUID


class EndGiveawayCallbackData(CallbackData, prefix="end_giveaway"):
    giveaway_id: UUID


def get_admin_menu_kb() -> InlineKeyboardMarkup:
    kb = [
        [
            InlineKeyboardButton(
                text="Создать розыгрыш",
                callback_data="giveaway:create"
            )
        ],
        [
            InlineKeyboardButton(
                text="Рассылка",
                callback_data="broadcast"
            )
        ],
        [
            InlineKeyboardButton(
                text="Управление розыгрышами",
                callback_data="giveaway:list"
            )
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)


def get_giveaway_list(giveaways: list[Giveaway]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    buttons = [
        InlineKeyboardButton(
            text=f"{giveaway.title}",
            callback_data=GiveawayInfoCallbackData(giveaway_id=giveaway.id).pack()
        )
        for giveaway in giveaways
    ]
    kb.row(*buttons, width=2)
    kb.row(
        InlineKeyboardButton(
            text="Назад",
            callback_data="admin:menu"
        )
    )
    return kb.as_markup()


def get_giveaway_info_kb(giveaway_id: UUID) -> InlineKeyboardMarkup:
    kb = [
        [
            InlineKeyboardButton(
                text="Продлить розыгрыш",
                callback_data=ExtendGiveawayCallbackData(giveaway_id=giveaway_id).pack()
            )
        ],
        # [
        #     InlineKeyboardButton(
        #         text="Изменить описание",
        #         callback_data=ChangeGiveawayDescriptionCallbackData(giveaway_id=giveaway_id).pack()
        #     )
        # ],
        # [
        #     InlineKeyboardButton(
        #         text="Завершить розыгрыш",
        #         callback_data=EndGiveawayCallbackData(giveaway_id=giveaway_id).pack()
        #     )
        # ],
        [
            InlineKeyboardButton(
                text="Назад",
                callback_data="giveaway:list"
            )
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)


def get_back_to_giveaway_info_kb(giveaway_id: UUID) -> InlineKeyboardMarkup:
    kb = [
        [
            InlineKeyboardButton(
                text="Назад",
                callback_data=GiveawayInfoCallbackData(giveaway_id=giveaway_id).pack()
            )
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def back_to_admin_menu() -> InlineKeyboardMarkup:
    kb = [
        [
            InlineKeyboardButton(
                text="Назад в админ-меню",
                callback_data="admin:menu"
            )
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)