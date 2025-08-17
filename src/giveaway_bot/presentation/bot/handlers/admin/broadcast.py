import asyncio
import logging
from collections import defaultdict
from dataclasses import dataclass
from io import BytesIO

from adaptix import Retort
from aiogram import Router, F
from aiogram import Bot as AiogramBot
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from dishka import FromDishka

from giveaway_bot.application.interfaces.dao.user import UserRepository
from giveaway_bot.presentation.bot.keyboard.admin.base import back_to_admin_menu
from giveaway_bot.presentation.bot.keyboard.admin.broadcast import URLButton, get_broadcast_confirmation_menu, \
    BroadcastAddButtonCallback, BroadcastCallbackData, get_broadcast_menu
from giveaway_bot.presentation.bot.utils.byte_utils import bytesio_to_base64, base64_to_bytes
from giveaway_bot.presentation.bot.utils.mailer import TGNotificator, MailingTaskDTO, MailingResult

router = Router(name=__name__)
logger = logging.getLogger(__name__)

retort = Retort()


def build_broadcast_keyboard(buttons: list[URLButton]) -> list[list[URLButton]] | None:
    """Build a keyboard from buttons."""
    if not buttons:
        return None

    row_map: dict[int, list[URLButton]] = defaultdict(list)
    for button in buttons:
        row_map[button.row].append(button)

    keyboard = []
    for row in sorted(row_map.keys()):
        row_maped = row_map[row]
        row_maped.sort(key=lambda x: x.column)
        keyboard.append(row_maped)
    return keyboard


class BroadcastState(StatesGroup):
    CREATE = State()
    ENTER_TEXT = State()
    ENTER_URL = State()


url_button_retort = Retort()


@router.callback_query(F.data == "broadcast")
async def broadcast_variants(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Выберите действие", reply_markup=get_broadcast_menu())
    await state.set_state(BroadcastState.CREATE)
    await state.update_data({"last_message_id": callback.message.message_id})


@router.callback_query(BroadcastCallbackData.filter())
async def broadcast_create(callback: CallbackQuery, callback_data: BroadcastCallbackData, state: FSMContext):
    await callback.message.delete_reply_markup()
    await callback.message.edit_text("Введите текст")
    await state.set_state(BroadcastState.CREATE)
    await state.update_data({"last_message_id": callback.message.message_id, "are_subscribed": callback_data.are_subscribed})


@router.message(BroadcastState.CREATE)
async def broadcast_cancel(message: Message, state: FSMContext, bot: AiogramBot):
    data = await state.get_data()
    last_message_id = data.get("last_message_id")
    await state.update_data({"broadcast_text": message.html_text})
    if message.photo:
        img_bytes = BytesIO()
        await bot.download(file=message.photo[-1].file_id, destination=img_bytes)
        await state.update_data({"photo": bytesio_to_base64(img_bytes), "text": message.caption})
    await message.delete()
    await bot.edit_message_text(
        "Выберите действие",
        chat_id=message.chat.id,
        message_id=last_message_id,
        reply_markup=get_broadcast_confirmation_menu()
    )


@router.callback_query(BroadcastAddButtonCallback.filter(), BroadcastState.CREATE)
async def add_url_button(callback: CallbackQuery, callback_data: BroadcastAddButtonCallback, state: FSMContext):
    row = callback_data.row
    column = callback_data.column
    await callback.message.edit_text(
        "Введите текст кнопки",
    )
    await state.set_state(BroadcastState.ENTER_TEXT)
    await state.update_data({"row": row, "column": column})


@router.message(BroadcastState.ENTER_TEXT)
async def add_url_button_text(message: Message, state: FSMContext, bot: AiogramBot):
    data = await state.get_data()
    last_message_id = data.get("last_message_id")
    text = message.text
    await state.update_data({"text": text})
    await message.delete()
    await bot.edit_message_text(
        "Введите URL",
        chat_id=message.chat.id,
        message_id=last_message_id,
    )
    await state.set_state(BroadcastState.ENTER_URL)


@router.message(BroadcastState.ENTER_URL)
async def add_url_button_url(message: Message, state: FSMContext, bot: AiogramBot):
    data = await state.get_data()
    last_message_id = data.get("last_message_id")
    url = message.text
    row = data.get("row")
    column = data.get("column")
    text = data.get("text")

    button = URLButton(
        text=text,
        url=url,
        row=row,
        column=column,
    )

    buttons_data = data.get("buttons", [])
    buttons_data.append(retort.dump(button))
    buttons = [retort.load(button_data, URLButton) for button_data in buttons_data]
    keyboard = build_broadcast_keyboard(buttons)

    await state.update_data({"buttons": [retort.dump(buttons) for buttons in buttons]})

    await message.delete()
    await state.set_state(BroadcastState.CREATE)
    await bot.edit_message_text(
        "Кнопка добавлена. Выберите действие",
        chat_id=message.chat.id,
        message_id=last_message_id,
        reply_markup=get_broadcast_confirmation_menu(keyboard)
    )


@router.callback_query(F.data == "broadcast:confirm", BroadcastState.CREATE)
async def broadcast_create(
        callback: CallbackQuery,
        state: FSMContext,
        bot: AiogramBot,
        user_repository: FromDishka[UserRepository],
):
    data = await state.get_data()
    text = data.get("broadcast_text")
    photo = data.get("photo")
    are_subscribed: bool | None = data.get("are_subscribed")
    buttons_data = data.get("buttons", [])
    buttons = retort.load(buttons_data, list[URLButton])
    keyboard = build_broadcast_keyboard(buttons)
    if photo:
        photo = base64_to_bytes(photo)
    if keyboard:
        keyboard = [
            [InlineKeyboardButton(text=button.text, url=button.url) for button in row]
            for row in keyboard
        ]
        reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    else:
        reply_markup = None

    await state.clear()
    await callback.message.edit_text("Рассылка запущена!", reply_markup=back_to_admin_menu())

    async def do_broadcast():
        mailer = TGNotificator(bot=bot, batch_size=30, send_interval=1)
        mailing_result = MailingResult()

        try:
            async for users_batch in user_repository.get_all(batch_size=1000, are_subscribed=are_subscribed):
                messages = []
                for user in users_batch:
                    messages.append(
                        MailingTaskDTO(
                            bot_id=bot.id,
                            chat_id=user.tg_id,
                            message=text,
                            media=photo,
                            keyboard_markup=reply_markup
                        )
                    )
                result = await mailer.send_notifications(messages)
                mailing_result += result

            await callback.message.answer(
                text=(
                    "<b>Рассылка завершена</b>\n"
                    f"📊 Обработано пользователей: {mailing_result.total}\n"
                    f"✅ Успешно отправлено сообщений: {mailing_result.success}\n"
                    f"❌ Недоставленных сообщений: {mailing_result.failed}"
                ),
                reply_markup=back_to_admin_menu(),
            )

        except Exception as e:
            logger.exception("Error during broadcast", exc_info=e)

    asyncio.create_task(do_broadcast())
