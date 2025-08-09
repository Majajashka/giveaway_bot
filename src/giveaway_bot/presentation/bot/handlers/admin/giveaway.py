from datetime import datetime, timedelta
from typing import BinaryIO
from zoneinfo import ZoneInfo

from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message
from dishka import FromDishka

from giveaway_bot.application.interactors.giveaway.create_giveaway import CreateGiveawayInteractor
from giveaway_bot.infrastructure.localization.translator import Localization
from giveaway_bot.presentation.bot.keyboard.admin.base import get_admin_menu_kb
from giveaway_bot.presentation.bot.utils.byte_utils import to_bytesio
from giveaway_bot.presentation.bot.utils.clock import LocalizedClock

router = Router(name=__name__)


class GiveawayCreateFSM(StatesGroup):
    TITLE_INPUT = State()
    DESCRIPTION_INPUT = State()
    DURATION_INPUT = State()


@router.callback_query(F.data == "giveaway:create")
async def start_giveaway_creation(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите название розыгрыша:")
    await state.set_state(GiveawayCreateFSM.TITLE_INPUT)
    await callback.answer()


@router.message(GiveawayCreateFSM.TITLE_INPUT)
async def process_title(message: Message, i18n: Localization, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer(
        text="Введите дату окончания в формате <b>ДД-ММ-ГГГГ ЧЧ:ММ</b> (например: <code>20-08-2025 18:30</code>)")
    await state.set_state(GiveawayCreateFSM.DURATION_INPUT)


@router.message(GiveawayCreateFSM.DURATION_INPUT)
async def process_duration(message: Message, i18n: Localization, state: FSMContext, clock: FromDishka[LocalizedClock]):
    text = message.text.strip()

    try:
        end_date = clock.parse_local_time_as_utc(text, template="%d-%m-%Y %H:%M")
        formatted = end_date.strftime("%d-%m-%Y %H:%M:%S")
        await state.update_data(end_date=formatted)
        await message.answer(
            text=(
                f"Дата окончания установлена: {clock.convert_utc_to_local(end_date)}\n\n"

                "Введите описание розыгрыша(с фото):"
            )
        )
        await state.set_state(GiveawayCreateFSM.DESCRIPTION_INPUT)
        return

    except ValueError:
        pass

    await message.answer(
        text=i18n("input-giveaway-duration")
    )


@router.message(F.photo, GiveawayCreateFSM.DESCRIPTION_INPUT)
async def process_description(message: Message, state: FSMContext, bot: Bot,
                              interactor: FromDishka[CreateGiveawayInteractor], clock: FromDishka[LocalizedClock]):
    data = await state.get_data()
    title: str = data.get("title")
    end_date: datetime = clock.parse_utc_time(data.get("end_date"))
    text: str = message.html_text
    photo = message.photo[-1]

    file = await bot.get_file(photo.file_id)
    file_path = file.file_path
    file_bytes: BinaryIO = await bot.download_file(file_path)
    giveaway = await interactor.execute(
        title=title,
        description=text,
        ends_at=end_date,
        media_data=to_bytesio(file_bytes),
    )
    bot_username = (await bot.get_me()).username
    await state.clear()
    await message.answer(
        text=(
            f"Розыгрыш успешно создан!\n"
            f"Ссылка: https://t.me/{bot_username}?start={giveaway.id}\n\n"
        ),
        reply_markup=get_admin_menu_kb()
    )
