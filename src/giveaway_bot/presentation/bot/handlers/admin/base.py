from aiogram import Router, F
from aiogram.filters import CommandObject, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from dishka import FromDishka

from giveaway_bot.application.interactors.giveaway.hide_integration import HideIntegrationInteractor
from giveaway_bot.infrastructure.database.gateways.settings import SettingsRepo
from giveaway_bot.presentation.bot.keyboard.admin.base import get_admin_menu_kb, HideIntegrationCallbackData

router = Router(name=__name__)


@router.message(Command("admin"))
async def admin_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Админ-меню:", reply_markup=get_admin_menu_kb())


@router.callback_query(F.data == "admin:menu")
async def admin_menu_handler(callback_query, state: FSMContext):
    await state.clear()
    await callback_query.message.edit_text("Админ-меню:", reply_markup=get_admin_menu_kb())
    await callback_query.answer()




