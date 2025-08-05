
from aiogram import Bot, Dispatcher
from dishka import AsyncContainer, make_async_container
from dishka.integrations.aiogram import AutoInjectMiddleware

from template.config import Config
from template.infrastructure.ioc.providers import get_aiogram_providers, get_providers
from template.presentation.bot.middlewares.container import ContainerMiddleware


def setup_container(config: Config) -> AsyncContainer:
    container = make_async_container(
        *get_aiogram_providers(),
        *get_providers(),
        context={
            Config: config,
        },
    )
    return container


def setup_middleware(
        *,
        dispatcher: Dispatcher,
        container: AsyncContainer,
) -> None:
    container_middleware = ContainerMiddleware(container=container)
    autoinject_middleware = AutoInjectMiddleware()

    dispatcher.update.outer_middleware(middleware=container_middleware)

    for update in dispatcher.resolve_used_update_types():
        if update != "update":
            dispatcher.observers[update].middleware(middleware=autoinject_middleware)


async def run_telegram_bot(config: Config) -> None:
    ioc = setup_container(config)
    dp = await ioc.get(Dispatcher)
    bot = await ioc.get(Bot)
    setup_middleware(dispatcher=dp, container=ioc)
    await bot.delete_webhook()
    await dp.start_polling(bot)
