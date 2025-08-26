from aiogram import Router, F
from aiogram.filters import CommandObject, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from dishka import FromDishka

from giveaway_bot.application.interactors.giveaway.get_stats import GetGiveawayStartInteractor
from giveaway_bot.application.interactors.giveaway.hide_integration import HideIntegrationInteractor
from giveaway_bot.infrastructure.database.gateways.settings import SettingsRepo
from giveaway_bot.presentation.bot.keyboard.admin.base import get_admin_menu_kb, HideIntegrationCallbackData
from giveaway_bot.presentation.bot.utils.text import format_stats_text

router = Router(name=__name__)


@router.message(Command("admin"))
async def admin_handler(message: Message, state: FSMContext, stats_interactor: FromDishka[GetGiveawayStartInteractor]):
    await state.clear()
    stats = await stats_interactor.execute()
    await message.answer(
        text=format_stats_text(stats=stats),
        reply_markup=get_admin_menu_kb())


@router.callback_query(F.data == "admin:menu")
async def admin_menu_handler(callback_query, state: FSMContext, stats_interactor: FromDishka[GetGiveawayStartInteractor]):
    await state.clear()
    stats = await stats_interactor.execute()
    await callback_query.message.edit_text(format_stats_text(stats=stats), reply_markup=get_admin_menu_kb())
    await callback_query.answer()




