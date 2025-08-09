from aiogram import Router, F

from .base import router as base_router
from .giveaway import router as giveaway_router
from .manage_giveaway import router as manage_giveaway_router
from .broadcast import router as broadcast_router


def get_router() -> Router:
    router = Router()
    admin_ids = [694294789, 5282150472]  # Replace with actual admin IDs
    router.message.filter(F.from_user.id.in_(admin_ids))
    router.callback_query.filter(F.from_user.id.in_(admin_ids))
    router.include_router(base_router)
    router.include_router(giveaway_router)
    router.include_router(manage_giveaway_router)
    router.include_router(broadcast_router)
    return router
