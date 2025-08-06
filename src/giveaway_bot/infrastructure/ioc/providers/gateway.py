from dishka import Provider, Scope, provide

from giveaway_bot.application.interfaces.dao.user import UserRepository
from giveaway_bot.infrastructure.database.gateways.user import UserRepositoryImpl


class GatewayProvider(Provider):
    scope = Scope.REQUEST
    user_repo = provide(provides=UserRepository, source=UserRepositoryImpl)
