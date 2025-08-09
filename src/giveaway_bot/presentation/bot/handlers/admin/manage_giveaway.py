import logging
from datetime import datetime
from uuid import UUID

from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message
from dishka import FromDishka

from giveaway_bot.application.interactors.giveaway.extend_giveaway import ExtendGiveawayInteractor
from giveaway_bot.application.interactors.giveaway.get_active_giveaway import GetActiveGiveawayInteractor
from giveaway_bot.application.interactors.giveaway.get_all_active_giveaway import GetAllActiveGiveawayInteractor
from giveaway_bot.entities.domain.giveaway import Giveaway
from giveaway_bot.infrastructure.localization.translator import Localization
from giveaway_bot.presentation.bot.keyboard.admin.base import get_giveaway_list, GiveawayInfoCallbackData, \
    get_giveaway_info_kb, ExtendGiveawayCallbackData, get_back_to_giveaway_info_kb
from giveaway_bot.presentation.bot.utils.clock import LocalizedClock

logger = logging.getLogger(__name__)
router = Router(name=__name__)


class ExtendGiveawayFSM(StatesGroup):
    INPUT = State()


def format_giveaway_text(giveaway: Giveaway, clock: LocalizedClock, i18n: Localization) -> str:
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
        description=giveaway.description,
        created_at=clock.convert_utc_to_local(giveaway.created_at),
        ends_at=clock.convert_utc_to_local(giveaway.ends_at),
        time_left=time_left,
    )
    return text


@router.callback_query(F.data == "giveaway:list")
async def list_giveaways_handler(callback: CallbackQuery, i18n: Localization,
                                 interactor: FromDishka[GetAllActiveGiveawayInteractor]):
    await callback.answer()
    giveaways = await interactor.execute()

    if not giveaways:
        await callback.answer("Нет активных розыгрышей.", show_alert=True)
        return

    await callback.message.edit_text(
        text=i18n("giveaway-list"),
        reply_markup=get_giveaway_list(giveaways)
    )


@router.callback_query(GiveawayInfoCallbackData.filter())
async def giveaway_info_handler(
        callback: CallbackQuery,
        callback_data: GiveawayInfoCallbackData,
        i18n: Localization,
        interactor: FromDishka[GetActiveGiveawayInteractor],
        localized_clock: FromDishka[LocalizedClock]
):
    await callback.answer()
    giveaway = await interactor.execute(giveaway_id=callback_data.giveaway_id)

    if not giveaway:
        await callback.answer("Розыгрыш не найден.", show_alert=True)
        return

    await callback.message.edit_text(
        text=format_giveaway_text(giveaway=giveaway, clock=localized_clock, i18n=i18n),
        reply_markup=get_giveaway_info_kb(giveaway.id)
    )


@router.callback_query(ExtendGiveawayCallbackData.filter())
async def extend_giveaway_handler(
        callback: CallbackQuery,
        state: FSMContext,
        callback_data: ExtendGiveawayCallbackData,
):
    await state.set_state(ExtendGiveawayFSM.INPUT)
    await state.update_data(giveaway_id=str(callback_data.giveaway_id), message_id=callback.message.message_id)
    await callback.answer()
    await callback.message.edit_text(
        "Введите новую дату окончания розыгрыша в формате 'ДД-ММ-ГГГГ ЧЧ:ММ' (например, '31-12-2026 23:59').",
        reply_markup=get_back_to_giveaway_info_kb(giveaway_id=callback_data.giveaway_id)
    )


@router.message(ExtendGiveawayFSM.INPUT, F.text)
async def extend_giveaway_input_handler(
        message: Message,
        state: FSMContext,
        i18n: Localization,
        bot: Bot,
        interactor: FromDishka[ExtendGiveawayInteractor],
        localized_clock: FromDishka[LocalizedClock],
):
    data = await state.get_data()
    logger.info(data)
    giveaway_id = UUID(data["giveaway_id"])
    message_id = int(data["message_id"])

    date = localized_clock.parse_local_time_as_utc(message.text)
    await message.delete()
    giveaway = await interactor.execute(giveaway_id=giveaway_id, date=date)
    await bot.edit_message_text(
        text=format_giveaway_text(giveaway=giveaway, clock=localized_clock, i18n=i18n),
        chat_id=message.from_user.id,
        message_id=message_id,
        reply_markup=get_giveaway_info_kb(giveaway.id)
    )
