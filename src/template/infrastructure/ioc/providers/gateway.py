from dishka import Scope, provide, Provider

from template.application.interfaces.dao.user import UserRepository
from template.infrastructure.database.gateways.user import UserRepositoryImpl


class GatewayProvider(Provider):
    scope = Scope.REQUEST
    user_repo = provide(provides=UserRepository, source=UserRepositoryImpl)
