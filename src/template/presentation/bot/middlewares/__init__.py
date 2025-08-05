from aiogram import Dispatcher

from .localization import LocalizationMiddleware


def setup_middlewares(dp: Dispatcher) -> None:
    dp.message.outer_middleware(LocalizationMiddleware())
    dp.callback_query.outer_middleware(LocalizationMiddleware())

