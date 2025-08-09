from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter

from .integration import router as integration_router


def setup() -> APIRouter:
    router = APIRouter(route_class=DishkaRoute)
    router.include_router(integration_router)
    return router
