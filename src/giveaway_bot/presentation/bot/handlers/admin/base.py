from aiogram import Router, F
from aiogram.filters import CommandObject, Command
from aiogram.types import Message

from giveaway_bot.presentation.bot.keyboard.admin.base import get_admin_menu_kb

router = Router(name=__name__)


@router.message(Command("admin"))
async def admin_handler(message: Message, command: CommandObject):
    await message.answer("Админ-меню:", reply_markup=get_admin_menu_kb())


@router.callback_query(F.data == "admin:menu")
async def admin_menu_handler(callback_query):
    await callback_query.message.edit_text("Админ-меню:", reply_markup=get_admin_menu_kb())
    await callback_query.answer()
