from aiogram import Router

from .base import router as base_router


def get_router() -> Router:
    router = Router()
    router.include_router(base_router)
    return router
