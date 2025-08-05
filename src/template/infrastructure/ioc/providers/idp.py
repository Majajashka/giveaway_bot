from dishka import Provider, Scope, provide

from template.application.interfaces.provider import IdentityProvider
from template.infrastructure.aiogram.idp import TGUserIdentityProvider


class IdPProvider(Provider):
    tg_idp = provide(TGUserIdentityProvider, provides=IdentityProvider, scope=Scope.REQUEST)
