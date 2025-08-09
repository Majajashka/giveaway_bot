from dishka import AsyncContainer, make_async_container
from fastapi import FastAPI

from giveaway_bot.config import Config
from giveaway_bot.infrastructure.ioc.providers import get_providers, get_aiogram_providers
from giveaway_bot.presentation.api.routes import setup
from dishka.integrations.fastapi import setup_dishka


def setup_container(config: Config) -> AsyncContainer:
    container = make_async_container(
        *get_providers(),
        *get_aiogram_providers(),
        context={
            Config: config,
        },
    )
    return container


def main(config: Config) -> FastAPI:
    app = FastAPI()
    app.include_router(setup())

    container = setup_container(config)
    setup_dishka(container, app)
    return app