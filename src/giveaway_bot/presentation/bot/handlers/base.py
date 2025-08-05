from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from giveaway_bot.infrastructure.localization.translator import Localization

router = Router(name=__name__)


@router.message(Command("start"))
async def hello_handler(message: Message, i18n: Localization):
    await message.reply(
        text=i18n("start", first_name=message.from_user.first_name)
    )
