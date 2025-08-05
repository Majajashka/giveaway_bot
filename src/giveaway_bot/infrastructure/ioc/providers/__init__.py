from dishka import Provider

from giveaway_bot.infrastructure.ioc.providers.bot import BotProvider, LocalizationProvider
from giveaway_bot.infrastructure.ioc.providers.config import ConfigProvider
from giveaway_bot.infrastructure.ioc.providers.database import DatabaseProvider
from giveaway_bot.infrastructure.ioc.providers.dispatcher import DpProvider
from giveaway_bot.infrastructure.ioc.providers.gateway import GatewayProvider
from giveaway_bot.infrastructure.ioc.providers.idp import IdPProvider
from giveaway_bot.infrastructure.ioc.providers.interactor import InteractorProvider


def get_providers() -> list[Provider]:
    return [
        DatabaseProvider(),
        ConfigProvider(),
        IdPProvider(),
        LocalizationProvider(),
        GatewayProvider(),
        InteractorProvider()
    ]


def get_aiogram_providers() -> list[Provider]:
    return [
        BotProvider(),
        DpProvider(),
    ]
