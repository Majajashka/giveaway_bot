from dishka import Provider

from template.infrastructure.ioc.providers.bot import BotProvider, LocalizationProvider
from template.infrastructure.ioc.providers.config import ConfigProvider
from template.infrastructure.ioc.providers.database import DatabaseProvider
from template.infrastructure.ioc.providers.dispatcher import DpProvider
from template.infrastructure.ioc.providers.gateway import GatewayProvider
from template.infrastructure.ioc.providers.idp import IdPProvider
from template.infrastructure.ioc.providers.interactor import InteractorProvider


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
