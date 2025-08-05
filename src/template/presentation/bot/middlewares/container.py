from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Chat, TelegramObject
from dishka import AsyncContainer

from template.entities.domain.user import User


def make_context(data: dict[str, Any]) -> dict[Any, Any]:
    context = {
        Bot: data.get("bot"),
        TelegramObject: data.get("event"),
        Chat: data.get("event_chat"),
        FSMContext: data.get("state"),
        User: data.get("event_from_user"),
    }
    return {key: value for key, value in context.items() if value is not True}


class ContainerMiddleware(BaseMiddleware):
    def __init__(self, container: AsyncContainer):
        self._container = container

    async def __call__(
            self,
            handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: dict[str, Any],
    ) -> Any:
        context = make_context(data)
        async with self._container(context=context) as container:
            data["dishka_container"] = container
            return await handler(event, data)
