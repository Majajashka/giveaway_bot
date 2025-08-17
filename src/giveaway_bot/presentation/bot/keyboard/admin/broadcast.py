from dataclasses import dataclass

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


@dataclass
class URLButton:
    text: str
    url: str
    row: int
    column: int


class BroadcastAddButtonCallback(CallbackData, prefix="broadcast_add_button"):
    row: int
    column: int


class BroadcastCallbackData(CallbackData, prefix="broadcast"):
    are_subscribed: bool | None


def build_add_button_kb(buttons: list[list[URLButton]] | None) -> list[list[InlineKeyboardButton]]:
    if not buttons:
        kb: list[list[InlineKeyboardButton]] = [
            [
                InlineKeyboardButton(
                    text="+",
                    callback_data=BroadcastAddButtonCallback(
                        row=1,
                        column=1,

                    ).pack()
                )
            ]
        ]
    else:
        kb: list[list[InlineKeyboardButton]] = []
        for row_index, button_row in enumerate(buttons):
            row = row_index + 1
            transformed_row = [
                InlineKeyboardButton(
                    text=button.text,
                    url=button.url,
                )
                for button in button_row
            ]
            transformed_row.append(
                InlineKeyboardButton(
                    text="+",
                    callback_data=BroadcastAddButtonCallback(
                        row=row,
                        column=button_row[-1].column + 1,
                    ).pack()
                )
            )
            kb.append(transformed_row)

        kb.append(
            [
                InlineKeyboardButton(
                    text="+",
                    callback_data=BroadcastAddButtonCallback(
                        row=len(buttons) + 1,
                        column=1,
                    ).pack()
                )
            ]
        )
    return kb


def get_broadcast_confirmation_menu(
        buttons: list[list[URLButton]] | None = None,
) -> InlineKeyboardMarkup:
    kb = [
        *build_add_button_kb(buttons),
        [
            InlineKeyboardButton(
                text="-----------------------------",
                callback_data="nothing"
            )

        ],
        [
            InlineKeyboardButton(
                text="Подтвердить 🚨",
                callback_data="broadcast:confirm",
            ),
            InlineKeyboardButton(
                text="Отменить ❌",
                callback_data="admin:menu",
            ),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)


def get_broadcast_menu() -> InlineKeyboardMarkup:
    kb = [
        [
            InlineKeyboardButton(
                text="Подписчикам",
                callback_data=BroadcastCallbackData(are_subscribed=True).pack(),
            ),
            InlineKeyboardButton(
                text="Неподписчикам",
                callback_data=BroadcastCallbackData(are_subscribed=False).pack(),
            )
        ],
        [
            InlineKeyboardButton(
                text="Всем",
                callback_data=BroadcastCallbackData(are_subscribed=None).pack(),
            ),
        ],
        [
            InlineKeyboardButton(
                text="Назад",
                callback_data="admin:menu",
            ),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)