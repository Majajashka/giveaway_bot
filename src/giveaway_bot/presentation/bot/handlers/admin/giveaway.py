import asyncio
import logging
from datetime import datetime, timedelta
from io import BytesIO
from typing import BinaryIO, Optional
from zoneinfo import ZoneInfo

from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton, BufferedInputFile, \
    InputMediaPhoto
from aiogram_album import AlbumMessage
from dishka import FromDishka

from giveaway_bot.application.interactors.giveaway.create_giveaway import CreateGiveawayInteractor, GiveawayStepDTO
from giveaway_bot.infrastructure.localization.translator import Localization
from giveaway_bot.infrastructure.media_storage import MediaStorage
from giveaway_bot.presentation.bot.keyboard.admin.base import get_admin_menu_kb, get_giveaway_info_kb, \
    get_back_to_giveaway_info_kb, back_to_admin_menu
from giveaway_bot.presentation.bot.keyboard.giveaway import get_giveaway_kb
from giveaway_bot.presentation.bot.utils.byte_utils import to_bytesio, bytesio_to_base64, base64_to_bytesio
from giveaway_bot.presentation.bot.utils.clock import LocalizedClock
from giveaway_bot.presentation.bot.utils.text import format_giveaway_text, try_delete_message

router = Router(name=__name__)
logger = logging.getLogger(__name__)


class GiveawayCreateFSM(StatesGroup):
    TITLE_INPUT = State()
    INTEGRATION_URL_INPUT = State()
    DESCRIPTION_INPUT = State()
    SUBSCRIPTION_INPUT = State()
    INTEGRATION_INPUT = State()
    SUCCESS_INPUT = State()


@router.callback_query(F.data == "giveaway:create")
async def start_giveaway_creation(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите название розыгрыша:", reply_markup=back_to_admin_menu())
    await state.set_state(GiveawayCreateFSM.TITLE_INPUT)
    await callback.answer()


@router.message(GiveawayCreateFSM.TITLE_INPUT)
async def process_title(message: Message, state: FSMContext):
    await state.set_state(GiveawayCreateFSM.INTEGRATION_URL_INPUT)
    await state.update_data(title=message.text)
    await message.answer(
        text="Введите ссылку интеграции:\n Пример: <code>https://justonesec.ru/stream/gw5000</code>",
        reply_markup=back_to_admin_menu()
    )


@router.message(GiveawayCreateFSM.INTEGRATION_URL_INPUT)
async def process_integration_url(message: Message, state: FSMContext):
    await state.update_data(integration_url=message.text)
    await state.set_state(GiveawayCreateFSM.DESCRIPTION_INPUT)
    await message.answer(
        text="Введите описание розыгрыша(с изображением):",
        reply_markup=back_to_admin_menu()
    )


async def save_media_to_state(state: FSMContext, step_name: str, message: Message):
    """Сохраняет медиа (фото, видео, документ) в state, в base64 виде."""
    data = await state.get_data()
    medias = data.get(f"{step_name}_media", [])
    file = await message.bot.download(message.photo[-1].file_id)
    bio = BytesIO(file.read())
    b64 = bytesio_to_base64(bio)
    medias.append(b64)
    await state.update_data({f"{step_name}_media": medias})


async def save_text_to_state(state: FSMContext, step_name: str, text: str):
    await state.update_data({step_name: text})


async def reset_media_in_state(state: FSMContext, step_name: str):
    pass
    # await state.update_data({f"{step_name}_media": []})


async def get_step_data(state: FSMContext, step_name: str) -> dict:
    data = await state.get_data()
    text: Optional[str] = data.get(step_name)
    medias_b64: Optional[list[str]] = data.get(f"{step_name}_media")
    medias_bytesio = [base64_to_bytesio(b64) for b64 in medias_b64] if medias_b64 else []
    return {"text": text, "media": medias_bytesio if medias_bytesio else None}


async def handle_step_text(
        message: Message,
        state: FSMContext,
        step_name: str,
        next_state: Optional[State],
        prompt_next: str,
        kb: InlineKeyboardMarkup | None = None
):
    await save_text_to_state(state, step_name, message.html_text)
    await reset_media_in_state(state, step_name)
    if message.photo:
        await save_media_to_state(state, step_name, message)
    if next_state:
        await message.answer(prompt_next, reply_markup=kb)
        await state.set_state(next_state)
        await reset_media_in_state(state, next_state.state.lower())


# --- Универсальный обработчик для медиагруппы (AlbumMessage) ---

async def handle_step_album(
        album: "AlbumMessage",
        state: FSMContext,
        step_name: str,
        next_state: Optional[State],
        prompt_next: str | None,
        kb: InlineKeyboardMarkup | None = None
):
    medias_b64 = []
    for msg in album.messages:
        file = await msg.bot.download(msg.photo[-1].file_id)
        bio = BytesIO(file.read())
        medias_b64.append(bytesio_to_base64(bio))
    text = album.messages[0].caption or ""
    await state.update_data({step_name: text, f"{step_name}_media": medias_b64})
    if next_state:
        await album.answer(prompt_next, reply_markup=kb)
        await state.set_state(next_state)
        await reset_media_in_state(state, next_state.state.lower())


def get_skip_kb() -> InlineKeyboardMarkup:
    kb = [
        [InlineKeyboardButton(text="Пропустить", callback_data="giveaway:create:skip")],
        [InlineKeyboardButton(text="Пропустить всё", callback_data="giveaway:create:skip_all")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)


# Media group handlers for media ha-ha
# without media group - for photo/only text

@router.message(GiveawayCreateFSM.DESCRIPTION_INPUT, F.media_group_id)
async def process_description_album(album: "AlbumMessage", state: FSMContext):
    await handle_step_album(
        album,
        state,
        "description_input",
        GiveawayCreateFSM.SUBSCRIPTION_INPUT,
        "Введите текст для меню с проверкой подписок:",
        kb=get_skip_kb()
    )


@router.message(GiveawayCreateFSM.DESCRIPTION_INPUT)
async def process_description_text(message: Message, state: FSMContext):
    if not message.photo:
        logger.info("User sent description without media")
        msg = await message.answer("Пришлите текст с фото!!!")
        await asyncio.sleep(3)
        await try_delete_message(msg)
        await asyncio.sleep(3)
        await try_delete_message(message)
        return
    await handle_step_text(
        message,
        state,
        "description_input",
        GiveawayCreateFSM.SUBSCRIPTION_INPUT,
        "Введите текст для меню с проверкой подписок:",
        kb=get_skip_kb()
    )


@router.message(GiveawayCreateFSM.SUBSCRIPTION_INPUT, F.media_group_id)
async def process_subscription_album(album: "AlbumMessage", state: FSMContext):
    logger.info("Processing description album")
    await handle_step_album(
        album,
        state,
        "subscription_input",
        GiveawayCreateFSM.INTEGRATION_INPUT,
        "Введите описание интеграции. Укажите {link}, которое заменится ссылку:",
        kb=get_skip_kb()
    )


@router.message(GiveawayCreateFSM.SUBSCRIPTION_INPUT)
async def process_subscription_text(message: Message, state: FSMContext):
    await handle_step_text(
        message,
        state,
        "subscription_input",
        GiveawayCreateFSM.INTEGRATION_INPUT,
        "Введите описание интеграции. Укажите {link}, которое заменится ссылку:",
        kb=get_skip_kb()
    )


@router.message(GiveawayCreateFSM.INTEGRATION_INPUT, F.media_group_id)
async def process_integration_album(album: "AlbumMessage", state: FSMContext):
    logger.info("Processing description album")
    await handle_step_album(
        album,
        state,
        "integration_input",
        GiveawayCreateFSM.SUCCESS_INPUT,
        "Введите текст успеха:",
        kb=get_skip_kb()
    )


@router.message(GiveawayCreateFSM.INTEGRATION_INPUT)
async def process_integration_text(message: Message, state: FSMContext):
    await handle_step_text(
        message,
        state,
        "integration_input",
        GiveawayCreateFSM.SUCCESS_INPUT,
        "Введите текст успеха:",
        kb=get_skip_kb()
    )


async def gather_all_data(state: FSMContext):
    keys = [
        "description_input",
        "subscription_input",
        "integration_input",
        "success_input",
    ]
    result = {}
    data = await state.get_data()
    result['title'] = data.get("title")
    result['integration_url'] = data.get("integration_url")
    for key in keys:
        text = data.get(key)
        if not text:
            continue
        medias_b64 = data.get(f"{key}_media", [])
        medias_bytesio = [base64_to_bytesio(b64) for b64 in medias_b64] if medias_b64 else None
        result[key] = GiveawayStepDTO(
            text=text,
            media=medias_bytesio,
        )
    return result


@router.message(GiveawayCreateFSM.SUCCESS_INPUT, F.media_group_id)
async def process_success_album(
        album: "AlbumMessage",
        state: FSMContext,
        interactor: FromDishka[CreateGiveawayInteractor],
        clock: FromDishka[LocalizedClock],
        i18n: Localization,
        bot: Bot,
        file_repo: FromDishka[MediaStorage],
):
    await handle_step_album(
        album,
        state,
        "success_input",
        None,
        ""
    )
    data = await gather_all_data(state)
    logger.info(data)
    username = (await bot.get_me()).username
    giveaway = await interactor.execute(
        title=data['title'],
        integration_url=data['integration_url'],
        description_step_data=data.get("description_input"),
        subscription_step_data=data.get("subscription_input"),
        integration_step_data=data.get("integration_input"),
        success_step_data=data.get("success_input"),
    )
    media_file = giveaway.description_step.media[0]
    bytes = await file_repo.get_media(media_file.filename)
    media = BufferedInputFile(bytes.read(), filename=media_file.filename)
    await album.answer_photo(
        photo=media,
        caption=format_giveaway_text(giveaway=giveaway, clock=clock, i18n=i18n,
                                     bot_username=username),
        reply_markup=get_giveaway_info_kb(giveaway.id, hide_integration=giveaway.hide_integration)
    )


@router.message(GiveawayCreateFSM.SUCCESS_INPUT)
async def process_success_text(
        message: Message,
        state: FSMContext,
        interactor: FromDishka[CreateGiveawayInteractor],
        clock: FromDishka[LocalizedClock],
        i18n: Localization,
        bot: Bot,
        file_repo: FromDishka[MediaStorage],
):
    await handle_step_text(
        message,
        state,
        "success_input",
        None,
        ""
    )
    data = await gather_all_data(state)
    logger.info(data)

    giveaway = await interactor.execute(
        title=data['title'],
        integration_url=data['integration_url'],
        description_step_data=data.get("description_input"),
        subscription_step_data=data.get("subscription_input"),
        integration_step_data=data.get("integration_input"),
        success_step_data=data.get("success_input"),
    )
    bot_username = (await bot.get_me()).username
    media_file = giveaway.description_step.media[0]
    bytes = await file_repo.get_media(media_file.filename)
    media = BufferedInputFile(bytes.read(), filename=media_file.filename)
    await message.answer_photo(
        photo=media,
        caption=format_giveaway_text(giveaway=giveaway, clock=clock, i18n=i18n,
                                     bot_username=bot_username),
        reply_markup=get_giveaway_info_kb(giveaway.id, hide_integration=giveaway.hide_integration)
    )
    await state.clear()


@router.callback_query(F.data == "giveaway:create:skip")
async def skip_step(
        callback: CallbackQuery,
        state: FSMContext,
        interactor: FromDishka[CreateGiveawayInteractor],
        clock: FromDishka[LocalizedClock],
        i18n: Localization,
        bot: Bot,
        file_repo: FromDishka[MediaStorage],
):
    current_state = await state.get_state()
    data = await gather_all_data(state)

    if current_state == GiveawayCreateFSM.INTEGRATION_INPUT.state:
        await state.set_state(GiveawayCreateFSM.SUCCESS_INPUT)
        await callback.message.answer("Введите текст успеха:")
    elif current_state == GiveawayCreateFSM.DESCRIPTION_INPUT.state:
        await state.set_state(GiveawayCreateFSM.SUBSCRIPTION_INPUT)
        await callback.message.answer("Введите описание подписки:")
    elif current_state == GiveawayCreateFSM.SUBSCRIPTION_INPUT.state:
        await state.set_state(GiveawayCreateFSM.INTEGRATION_INPUT)
        await callback.message.answer("Введите описание интеграции:")
    elif current_state == GiveawayCreateFSM.SUCCESS_INPUT.state:
        giveaway = await interactor.execute(
            title=data['title'],
            integration_url=data['integration_url'],
            description_step_data=data.get("description_input"),
            subscription_step_data=data.get("subscription_input"),
            integration_step_data=data.get("integration_input"),
            success_step_data=data.get("success_input"),
        )
        bot_username = (await bot.get_me()).username
        media_file = giveaway.description_step.media[0]
        bytes = await file_repo.get_media(media_file.filename)
        media = BufferedInputFile(bytes.read(), filename=media_file.filename)
        await callback.message.answer_photo(
            photo=media,
            caption=format_giveaway_text(giveaway=giveaway, clock=clock, i18n=i18n,
                                         bot_username=bot_username),
            reply_markup=get_giveaway_info_kb(giveaway.id, hide_integration=giveaway.hide_integration)
        )
        await state.clear()
    else:
        await callback.answer("Невозможно пропустить этот шаг.")
    await callback.answer()


@router.callback_query(F.data == "giveaway:create:skip_all")
async def skip_step(callback: CallbackQuery, state: FSMContext, interactor: FromDishka[CreateGiveawayInteractor],
                    clock: FromDishka[LocalizedClock], file_repo: FromDishka[MediaStorage],
                    i18n: Localization, bot: Bot):
    data = await gather_all_data(state)
    logger.info(data)
    giveaway = await interactor.execute(
        title=data['title'],
        integration_url=data['integration_url'],
        description_step_data=data.get("description_input"),
        subscription_step_data=data.get("subscription_input"),
        integration_step_data=data.get("integration_input"),
        success_step_data=data.get("success_input"),
    )
    bot_username = (await bot.get_me()).username
    media_file = giveaway.description_step.media[0]
    bytes = await file_repo.get_media(media_file.filename)
    media = BufferedInputFile(bytes.read(), filename=media_file.filename)
    await callback.message.answer_photo(
        photo=media,
        caption=format_giveaway_text(giveaway=giveaway, clock=clock, i18n=i18n,
                                     bot_username=bot_username),
        reply_markup=get_giveaway_info_kb(giveaway.id, hide_integration=giveaway.hide_integration)
    )
    await state.clear()

# @router.message(F.photo, GiveawayCreateFSM.DESCRIPTION_INPUT)
# async def process_description(message: Message, state: FSMContext, bot: Bot,
#                               interactor: FromDishka[CreateGiveawayInteractor], clock: FromDishka[LocalizedClock]):
#     data = await state.get_data()
#     title: str = data.get("title")
#     end_date: datetime = clock.parse_utc_time(data.get("end_date"))
#     text: str = message.html_text
#     photo = message.photo[-1]
#
#     file = await bot.get_file(photo.file_id)
#     file_path = file.file_path
#     file_bytes: BinaryIO = await bot.download_file(file_path)
#     giveaway = await interactor.execute(
#         title=title,
#         description=text,
#         ends_at=end_date,
#         media_data=to_bytesio(file_bytes),
#     )
#     bot_username = (await bot.get_me()).username
#     await state.clear()
#     await message.answer(
#         text=(
#             f"Розыгрыш успешно создан!\n"
#             f"Ссылка: https://t.me/{bot_username}?start={giveaway.id}\n\n"
#         ),
#         reply_markup=get_admin_menu_kb()
#     )
