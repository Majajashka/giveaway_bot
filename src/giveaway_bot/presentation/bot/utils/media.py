from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InputMediaPhoto, BufferedInputFile

from giveaway_bot.entities.domain.giveaway import GiveawayStep
from giveaway_bot.infrastructure.media_storage import MediaStorage


async def answer_by_media(
        event: CallbackQuery | Message,
        step: GiveawayStep,
        file_repo: MediaStorage,
        kb: InlineKeyboardMarkup | None = None
):
    if isinstance(event, CallbackQuery):
        message = event.message
    else:
        message = event
    text = step.text
    if step.media:
        medias = []
        for media in step.media:
            file_bytes = await file_repo.get_media(media.filename)
            file_bytes.seek(0)
            medias.append(
                InputMediaPhoto(
                    media=BufferedInputFile(file=file_bytes.read(), filename=media.filename),
                    caption=text if len(medias) == 0 else None)
            )
        if len(medias) == 1:
            msg = await message.answer_photo(photo=medias[0].media, caption=text, reply_markup=kb)
            return msg.message_id
        else:
            await message.answer_media_group(media=medias, reply_markup=kb)
    else:
        await message.answer(text=text, reply_markup=kb)


async def edit_by_media(
        event: CallbackQuery | Message,
        step: GiveawayStep,
        file_repo: MediaStorage,
        kb: InlineKeyboardMarkup | None = None
):
    if isinstance(event, CallbackQuery):
        message = event.message
    else:
        message = event
    text = step.text
    if step.media:
        medias = []
        for media in step.media:
            file_bytes = await file_repo.get_media(media.filename)
            file_bytes.seek(0)
            medias.append(
                InputMediaPhoto(
                    media=BufferedInputFile(file=file_bytes.read(), filename=media.filename),
                    caption=text if len(medias) == 0 else None)
            )
        await message.answer_media_group(media=medias, reply_markup=kb)
    else:
        await message.answer(text=text, reply_markup=kb)
