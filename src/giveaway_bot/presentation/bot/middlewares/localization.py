from collections.abc import Awaitable, Callable
from typing import Any

from aiogram.types import CallbackQuery, Message, TelegramObject
from dishka import AsyncContainer

from giveaway_bot.application.dtos.user import UserCreateDTO
from giveaway_bot.application.interactors.user.get_or_create_user_interactor import GetOrCreateUserInteractor
from giveaway_bot.infrastructure.localization.translator import LocalizationStorage


class LocalizationMiddleware:

    async def __call__(
            self,
            handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
            event: Message | CallbackQuery,
            data: dict[str, Any],
    ) -> Any:
        container: AsyncContainer = data["dishka_container"]
        localization_storage = await container.get(LocalizationStorage)
        user_interactor = await container.get(GetOrCreateUserInteractor)
        user = await user_interactor.execute(
            data=UserCreateDTO(
                tg_id=event.from_user.id,
                username=event.from_user.username,
            ),
        )
        data["i18n"] = localization_storage.get_locale(user.language.value)

        return await handler(event, data)

