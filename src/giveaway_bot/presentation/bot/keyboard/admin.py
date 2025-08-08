from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


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
                text="Управление розыгрышами",
                callback_data="manage_giveaways"
            )
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)
