import logging
from datetime import datetime
from io import BytesIO
from uuid import UUID

from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message, BufferedInputFile, InputMediaPhoto
from dishka import FromDishka

from giveaway_bot.application.dtos.giveaway import GiveawayStepDTO
from giveaway_bot.application.interactors.giveaway.edit_giveaway_step import EditGiveawayStepInteractor
from giveaway_bot.application.interactors.giveaway.edit_url import EditGiveawayIntegrationUrlInteractor
from giveaway_bot.application.interactors.giveaway.extend_giveaway import ExtendGiveawayInteractor
from giveaway_bot.application.interactors.giveaway.get_active_giveaway import GetActiveGiveawayInteractor
from giveaway_bot.application.interactors.giveaway.get_all_active_giveaway import GetAllActiveGiveawayInteractor
from giveaway_bot.application.interactors.giveaway.get_giveaway_steps import GetGiveawayStepsInteractor
from giveaway_bot.application.interactors.giveaway.hide_integration import HideIntegrationInteractor
from giveaway_bot.entities.domain.giveaway import Giveaway
from giveaway_bot.infrastructure.localization.translator import Localization
from giveaway_bot.infrastructure.media_storage import MediaStorage
from giveaway_bot.presentation.bot.keyboard.admin.base import get_giveaway_list, GiveawayInfoCallbackData, \
    get_giveaway_info_kb, ExtendGiveawayCallbackData, get_back_to_giveaway_info_kb, \
    ChangeGiveawayIntegrationMenuCallbackData, ChangeGiveawayDescriptionCallbackData, \
    ChangeGiveawaySubscriptionMenuCallbackData, ChangeGiveawaySuccessMenuCallbackData, HideIntegrationCallbackData, \
    ChangeIntegrationURLCallbackData
from giveaway_bot.presentation.bot.utils.clock import LocalizedClock
from giveaway_bot.presentation.bot.utils.media import answer_by_media
from giveaway_bot.presentation.bot.utils.text import try_delete_message, format_giveaway_text

logger = logging.getLogger(__name__)
router = Router(name=__name__)


class ExtendGiveawayFSM(StatesGroup):
    INPUT = State()


class ChangeGiveawaySubscriptionMenuFSM(StatesGroup):
    INPUT = State()


class ChangeGiveawayIntegrationMenuFSM(StatesGroup):
    INPUT = State()


class ChangeGiveawaySuccessMenuMenuFSM(StatesGroup):
    INPUT = State()


class ChangeGiveawayDescriptionMenuFSM(StatesGroup):
    INPUT = State()


class EditGiveawayIntegrationUrlFSM(StatesGroup):
    INPUT = State()




@router.callback_query(F.data == "giveaway:list")
async def list_giveaways_handler(callback: CallbackQuery, i18n: Localization,
                                 interactor: FromDishka[GetAllActiveGiveawayInteractor]):
    await callback.answer()
    giveaways = await interactor.execute()

    if not giveaways:
        await callback.answer("Нет активных розыгрышей.", show_alert=True)
        return

    if callback.message.photo:
        await callback.message.delete()
        await callback.message.answer(
            text=i18n("giveaway-list"),
            reply_markup=get_giveaway_list(giveaways)
        )
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
        localized_clock: FromDishka[LocalizedClock],
        file_repo: FromDishka[MediaStorage],
        bot: Bot
):
    await callback.answer()
    giveaway = await interactor.execute(giveaway_id=callback_data.giveaway_id)

    if not giveaway:
        await callback.answer("Розыгрыш не найден.", show_alert=True)
        return

    bot_username = (await bot.get_me()).username

    media_file = giveaway.description_step.media[0]
    bytes = await file_repo.get_media(media_file.filename)
    media = BufferedInputFile(bytes.read(), filename=media_file.filename)
    await callback.message.edit_media(
        media=InputMediaPhoto(
            media=media,
            caption=format_giveaway_text(giveaway=giveaway, clock=localized_clock, i18n=i18n,
                                         bot_username=bot_username),
        ),
        reply_markup=get_giveaway_info_kb(giveaway.id, hide_integration=giveaway.hide_integration)
    )


# @router.callback_query(ExtendGiveawayCallbackData.filter())
# async def extend_giveaway_handler(
#         callback: CallbackQuery,
#         state: FSMContext,
#         callback_data: ExtendGiveawayCallbackData,
# ):
#     await state.set_state(ExtendGiveawayFSM.INPUT)
#     await state.update_data(giveaway_id=str(callback_data.giveaway_id), message_id=callback.message.message_id)
#     await callback.answer()
#     await callback.message.edit_text(
#         "Введите новую дату окончания розыгрыша в формате 'ДД-ММ-ГГГГ ЧЧ:ММ' (например, '31-12-2026 23:59').",
#         reply_markup=get_back_to_giveaway_info_kb(giveaway_id=callback_data.giveaway_id)
#     )
#
#
# @router.message(ExtendGiveawayFSM.INPUT, F.text)
# async def extend_giveaway_input_handler(
#         message: Message,
#         state: FSMContext,
#         i18n: Localization,
#         bot: Bot,
#         interactor: FromDishka[ExtendGiveawayInteractor],
#         localized_clock: FromDishka[LocalizedClock],
# ):
#     data = await state.get_data()
#     logger.info(data)
#     giveaway_id = UUID(data["giveaway_id"])
#     message_id = int(data["message_id"])
#
#     date = localized_clock.parse_local_time_as_utc(message.text)
#     await message.delete()
#     giveaway = await interactor.execute(giveaway_id=giveaway_id, date=date)
#     bot_username = (await bot.get_me()).username
#
#     await bot.edit_message_text(
#         text=format_giveaway_text(giveaway=giveaway, clock=localized_clock, i18n=i18n, bot_username=bot_username),
#         chat_id=message.from_user.id,
#         message_id=message_id,
#         reply_markup=get_giveaway_info_kb(giveaway.id)
#     )


# ===== Изменение описания =====
@router.callback_query(ChangeGiveawayDescriptionCallbackData.filter())
async def change_giveaway_description_handler(
        callback: CallbackQuery,
        state: FSMContext,
        callback_data: ChangeGiveawayDescriptionCallbackData,
        interactor: FromDishka[GetGiveawayStepsInteractor],
        file_repo: FromDishka[MediaStorage],

):
    steps = await interactor.execute(callback_data.giveaway_id, user_id=callback.from_user.id)
    await state.set_state(ChangeGiveawayDescriptionMenuFSM.INPUT)

    await answer_by_media(
        event=callback,
        step=steps.description_step,
        file_repo=file_repo,
    )
    await callback.answer()
    clbk = await callback.message.answer(
        "Введите новое описание розыгрыша:",
        reply_markup=get_back_to_giveaway_info_kb(callback_data.giveaway_id)
    )
    await state.update_data(giveaway_id=str(callback_data.giveaway_id),
                            message_id=callback.message.message_id, clbk_msg_id=clbk.message_id)

@router.message(ChangeGiveawayDescriptionMenuFSM.INPUT)
async def change_giveaway_description_input_handler(
        message: Message,
        state: FSMContext,
        i18n: Localization,
        bot: Bot,
        interactor: FromDishka[EditGiveawayStepInteractor],  # должен быть твой интерактор
        localized_clock: FromDishka[LocalizedClock],
        file_repo: FromDishka[MediaStorage],
):
    data = await state.get_data()
    giveaway_id = UUID(data["giveaway_id"])
    message_id = int(data["message_id"])
    clbk_msg_id = int(data["clbk_msg_id"])

    await message.delete()
    text = message.html_text
    file = None
    if message.photo:
        file = await message.bot.download(message.photo[-1].file_id)
    step = GiveawayStepDTO(
        text=text,
        media=[file] if file else None
    )
    logger.info(step)
    giveaway = await interactor.execute(
        giveaway_id=giveaway_id,
        step_type="description",
        giveaway_step=step,
    )
    bot_username = (await bot.get_me()).username
    await bot.delete_message(chat_id=message.from_user.id, message_id=message_id)
    await bot.delete_message(chat_id=message.from_user.id, message_id=clbk_msg_id)
    media_file = giveaway.description_step.media[0]
    bytes = await file_repo.get_media(media_file.filename)
    media = BufferedInputFile(bytes.read(), filename=media_file.filename)
    await message.answer_photo(
        photo=media,
        caption=format_giveaway_text(giveaway=giveaway, clock=localized_clock, i18n=i18n,
                                     bot_username=bot_username),
        reply_markup=get_giveaway_info_kb(giveaway.id, hide_integration=giveaway.hide_integration)
    )


# ===== Изменение меню подписки =====
@router.callback_query(ChangeGiveawaySubscriptionMenuCallbackData.filter())
async def change_giveaway_subscription_handler(
        callback: CallbackQuery,
        state: FSMContext,
        callback_data: ChangeGiveawaySubscriptionMenuCallbackData,
        interactor: FromDishka[GetGiveawayStepsInteractor],
        file_repo: FromDishka[MediaStorage],
):
    steps = await interactor.execute(callback_data.giveaway_id, user_id=callback.from_user.id)
    await state.set_state(ChangeGiveawaySubscriptionMenuFSM.INPUT)
    await state.update_data(giveaway_id=str(callback_data.giveaway_id),
                            message_id=callback.message.message_id)
    await answer_by_media(
        event=callback,
        step=steps.subscription_step,
        file_repo=file_repo,
    )
    await callback.answer()
    await callback.message.answer(
        "Введите новый текст для меню подписки:",
        reply_markup=get_back_to_giveaway_info_kb(callback_data.giveaway_id)
    )


@router.message(ChangeGiveawaySubscriptionMenuFSM.INPUT)
async def change_giveaway_subscription_input_handler(
        message: Message,
        state: FSMContext,
        i18n: Localization,
        bot: Bot,
        interactor: FromDishka[EditGiveawayStepInteractor],
        localized_clock: FromDishka[LocalizedClock],
        file_repo: FromDishka[MediaStorage],
):
    data = await state.get_data()
    giveaway_id = UUID(data["giveaway_id"])
    message_id = int(data["message_id"])

    await message.delete()
    text = message.html_text
    file = None
    if message.photo:
        file = await message.bot.download(message.photo[-1].file_id)
    step = GiveawayStepDTO(
        text=text,
        media=[file] if file else None
    )

    giveaway = await interactor.execute(
        giveaway_id=giveaway_id,
        step_type="subscription",
        giveaway_step=step,
    )
    await bot.delete_message(chat_id=message.from_user.id, message_id=message_id)

    bot_username = (await bot.get_me()).username

    media_file = giveaway.description_step.media[0]
    bytes = await file_repo.get_media(media_file.filename)
    media = BufferedInputFile(bytes.read(), filename=media_file.filename)
    await message.answer_photo(
        photo=media,
        caption=format_giveaway_text(giveaway=giveaway, clock=localized_clock, i18n=i18n,
                                     bot_username=bot_username),
        reply_markup=get_giveaway_info_kb(giveaway.id, hide_integration=giveaway.hide_integration)
    )

# ===== Изменение меню интеграции =====
@router.callback_query(ChangeGiveawayIntegrationMenuCallbackData.filter())
async def change_giveaway_integration_handler(
        callback: CallbackQuery,
        state: FSMContext,
        callback_data: ChangeGiveawayIntegrationMenuCallbackData,
        interactor: FromDishka[GetGiveawayStepsInteractor],
        file_repo: FromDishka[MediaStorage],
):
    steps = await interactor.execute(callback_data.giveaway_id, user_id=callback.from_user.id)

    await state.set_state(ChangeGiveawayIntegrationMenuFSM.INPUT)
    await state.update_data(giveaway_id=str(callback_data.giveaway_id),
                            message_id=callback.message.message_id)
    await answer_by_media(
        event=callback,
        step=steps.integration_step,
        file_repo=file_repo,
    )
    await callback.answer()
    await callback.message.answer(
        "Введите новый текст для меню интеграции:",
        reply_markup=get_back_to_giveaway_info_kb(callback_data.giveaway_id)
    )



@router.message(ChangeGiveawayIntegrationMenuFSM.INPUT)
async def change_giveaway_integration_input_handler(
        message: Message,
        state: FSMContext,
        i18n: Localization,
        bot: Bot,
        interactor: FromDishka[EditGiveawayStepInteractor],
        localized_clock: FromDishka[LocalizedClock],
        file_repo: FromDishka[MediaStorage],
):
    data = await state.get_data()
    giveaway_id = UUID(data["giveaway_id"])
    message_id = int(data["message_id"])

    await message.delete()
    text = message.html_text
    file = None
    if message.photo:
        file = await message.bot.download(message.photo[-1].file_id)
    step = GiveawayStepDTO(
        text=text,
        media=[file] if file else None
    )
    giveaway = await interactor.execute(
        giveaway_id=giveaway_id,
        step_type="integration",
        giveaway_step=step,
    )
    await bot.delete_message(chat_id=message.from_user.id, message_id=message_id)

    bot_username = (await bot.get_me()).username

    media_file = giveaway.description_step.media[0]
    bytes = await file_repo.get_media(media_file.filename)
    media = BufferedInputFile(bytes.read(), filename=media_file.filename)
    await message.answer_photo(
        photo=media,
        caption=format_giveaway_text(giveaway=giveaway, clock=localized_clock, i18n=i18n,
                                     bot_username=bot_username),
        reply_markup=get_giveaway_info_kb(giveaway.id, hide_integration=giveaway.hide_integration)
    )


# ===== Изменение меню участия =====
@router.callback_query(ChangeGiveawaySuccessMenuCallbackData.filter())
async def change_giveaway_success_handler(
        callback: CallbackQuery,
        state: FSMContext,
        callback_data: ChangeGiveawaySuccessMenuCallbackData,
        interactor: FromDishka[GetGiveawayStepsInteractor],
        file_repo: FromDishka[MediaStorage],
):
    steps = await interactor.execute(callback_data.giveaway_id, user_id=callback.from_user.id)

    await state.set_state(ChangeGiveawaySuccessMenuMenuFSM.INPUT)
    await state.update_data(giveaway_id=str(callback_data.giveaway_id),
                            message_id=callback.message.message_id)
    await answer_by_media(
        event=callback,
        step=steps.success_step,
        file_repo=file_repo,
    )
    await callback.answer()
    await callback.message.answer(
        "Введите новый текст для меню участия:",
        reply_markup=get_back_to_giveaway_info_kb(callback_data.giveaway_id)
    )



@router.message(ChangeGiveawaySuccessMenuMenuFSM.INPUT)
async def change_giveaway_success_input_handler(
        message: Message,
        state: FSMContext,
        i18n: Localization,
        bot: Bot,
        interactor: FromDishka[EditGiveawayStepInteractor],
        localized_clock: FromDishka[LocalizedClock],
        file_repo: FromDishka[MediaStorage]
):
    data = await state.get_data()
    giveaway_id = UUID(data["giveaway_id"])
    message_id = int(data["message_id"])

    await message.delete()
    text = message.html_text
    file = None
    if message.photo:
        file: BytesIO = await message.bot.download(message.photo[-1].file_id)
    step = GiveawayStepDTO(
        text=text,
        media=[file] if file else None
    )
    giveaway = await interactor.execute(
        giveaway_id=giveaway_id,
        step_type="success",
        giveaway_step=step,
    )
    await bot.delete_message(chat_id=message.from_user.id, message_id=message_id)

    bot_username = (await bot.get_me()).username

    media_file = giveaway.description_step.media[0]
    bytes = await file_repo.get_media(media_file.filename)
    media = BufferedInputFile(bytes.read(), filename=media_file.filename)
    await message.answer_photo(
        photo=media,
        caption=format_giveaway_text(giveaway=giveaway, clock=localized_clock, i18n=i18n,
                                     bot_username=bot_username),
        reply_markup=get_giveaway_info_kb(giveaway.id, hide_integration=giveaway.hide_integration)
    )


@router.callback_query(HideIntegrationCallbackData.filter())
async def hide_integration_handler(
        callback_query: CallbackQuery,
        callback_data: HideIntegrationCallbackData,
        state: FSMContext,
        interactor: FromDishka[HideIntegrationInteractor],
        i18n: Localization,
        bot: Bot,
        localized_clock: FromDishka[LocalizedClock],
):
    await state.clear()
    giveaway = await interactor.execute(giveaway_id=callback_data.giveaway_id)
    await callback_query.answer()
    bot_username = (await bot.get_me()).username
    await callback_query.message.edit_caption(
        caption=format_giveaway_text(giveaway=giveaway, clock=localized_clock, i18n=i18n,
                                     bot_username=bot_username),
        reply_markup=get_giveaway_info_kb(giveaway.id, hide_integration=giveaway.hide_integration)
    )


@router.callback_query(ChangeIntegrationURLCallbackData.filter())
async def hide_integration_handler(
        callback_query: CallbackQuery,
        callback_data: HideIntegrationCallbackData,
        state: FSMContext,
):
    await state.set_state(EditGiveawayIntegrationUrlFSM.INPUT)
    await state.update_data(giveaway_id=str(callback_data.giveaway_id),
                            message_id=callback_query.message.message_id)
    await callback_query.answer()
    if callback_query.message.caption:
        await callback_query.message.edit_caption(
            caption="Введите новый URL интеграции:",
            reply_markup=get_back_to_giveaway_info_kb(callback_data.giveaway_id)
        )
    else:
        await callback_query.message.edit_text(
            text="Введите новый URL интеграции:",
            reply_markup=get_back_to_giveaway_info_kb(callback_data.giveaway_id)
        )


@router.message(EditGiveawayIntegrationUrlFSM.INPUT)
async def hide_integration_handler(
        message: Message,
        state: FSMContext,
        interactor: FromDishka[EditGiveawayIntegrationUrlInteractor],
        i18n: Localization,
        bot: Bot,
        localized_clock: FromDishka[LocalizedClock],
        file_repo: FromDishka[MediaStorage],
):
    data = await state.get_data()
    giveaway_id = UUID(data["giveaway_id"])
    message_id = int(data["message_id"])

    giveaway = await interactor.execute(giveaway_id=giveaway_id, url=message.text)
    bot_username = (await bot.get_me()).username
    await message.delete()
    media_file = giveaway.description_step.media[0]
    bytes = await file_repo.get_media(media_file.filename)
    media = BufferedInputFile(bytes.read(), filename=media_file.filename)
    await bot.edit_message_media(
        chat_id=message.from_user.id,
        message_id=message_id,
        media=InputMediaPhoto(
            media=media,
            caption=format_giveaway_text(giveaway=giveaway, clock=localized_clock, i18n=i18n,
                                         bot_username=bot_username),
        ),
        reply_markup=get_giveaway_info_kb(giveaway.id, hide_integration=giveaway.hide_integration)
    )
