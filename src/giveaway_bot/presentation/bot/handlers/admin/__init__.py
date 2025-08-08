from aiogram import Router

from .base import router as base_router
from .giveaway import router as giveaway_router


def get_router() -> Router:
    router = Router()
    router.include_router(base_router)
    router.include_router(giveaway_router)
    return router