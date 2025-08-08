from aiogram import Router
from aiogram.filters import CommandObject, Command
from aiogram.types import Message

from giveaway_bot.presentation.bot.keyboard.admin import get_admin_menu_kb

router = Router(name=__name__)


@router.message(Command("admin"))
async def admin_handler(message: Message, command: CommandObject):
    """
    Handler for the /admin command.
    This command is intended for administrative tasks.
    """
    await message.answer("Админ-меню:", reply_markup=get_admin_menu_kb())
