from aiogram import Dispatcher
from aiogram_album.count_check_middleware import CountCheckAlbumMiddleware

from .localization import LocalizationMiddleware
from .media_group import LockAlbumMiddleware, DebugAlbumMiddleware


def setup_middlewares(dp: Dispatcher) -> None:
    # DebugAlbumMiddleware(router=dp, latency=1)
    CountCheckAlbumMiddleware(latency=1, router=dp)
    dp.message.outer_middleware(LocalizationMiddleware())
    dp.callback_query.outer_middleware(LocalizationMiddleware())

