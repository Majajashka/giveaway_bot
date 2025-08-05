from dishka import Provider, Scope, provide

from giveaway_bot.application.interfaces.provider import IdentityProvider
from giveaway_bot.infrastructure.aiogram.idp import TGUserIdentityProvider


class IdPProvider(Provider):
    tg_idp = provide(TGUserIdentityProvider, provides=IdentityProvider, scope=Scope.REQUEST)
