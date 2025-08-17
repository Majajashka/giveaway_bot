import logging
from uuid import UUID

from aiogram import Router
from aiogram.filters import CommandObject, CommandStart
from aiogram.types import BufferedInputFile, Message, InputMediaPhoto
from dishka import FromDishka

from giveaway_bot.application.interactors.giveaway.get_active_giveaway import GetActiveGiveawayInteractor
from giveaway_bot.application.interactors.giveaway.get_giveaway_steps import GetGiveawayStepsInteractor
from giveaway_bot.common.utils import is_uuid
from giveaway_bot.infrastructure.localization.translator import Localization
from giveaway_bot.infrastructure.media_storage import MediaStorage
from giveaway_bot.presentation.bot.keyboard.giveaway import get_giveaway_kb
from giveaway_bot.presentation.bot.utils.media import answer_by_media

router = Router(name=__name__)
logger = logging.getLogger(__name__)


@router.message(CommandStart(deep_link=True))
async def hello_handler(
        message: Message,
        command: CommandObject,
        i18n: Localization,
        interactor: FromDishka[GetGiveawayStepsInteractor],
        file_repo: FromDishka[MediaStorage]
):
    if not is_uuid(command.args):
        logger.info(
            f"User {message.from_user.id} tried to start the bot with an invalid deep link: {command.args}"
        )
        await message.reply(text=i18n("giveaway_not_found"))
        return

    giveaway_id = UUID(command.args)
    giveaway_steps = await interactor.execute(giveaway_id)
    step = giveaway_steps.description_step
    if not step:
        logger.info(
            f"User {message.from_user.id} tried to start the bot with a non-existing giveaway ID: {giveaway_id}"
        )
        await message.reply(text=i18n("giveaway_not_found"))
        return

    kb = get_giveaway_kb(giveaway_id=giveaway_id)

    await answer_by_media(
        event=message,
        step=step,
        file_repo=file_repo,
        kb=kb
    )
    logger.info(
        f"User {message.from_user.id} started the bot with giveaway ID: {giveaway_id}"
    )


@router.message(CommandStart())
async def hello_handler(message: Message, i18n: Localization):
    logger.info(
        f"User {message.from_user.id} started the bot without a deep link."
    )
    return await message.answer(text=i18n("start", first_name=message.from_user.first_name))
