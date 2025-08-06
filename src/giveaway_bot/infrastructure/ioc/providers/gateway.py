from dishka import Provider, Scope, provide

from giveaway_bot.application.interfaces.dao.media import MediaRepository
from giveaway_bot.application.interfaces.dao.user import UserRepository
from giveaway_bot.infrastructure.database.gateways.media import MediaRepositoryImpl
from giveaway_bot.infrastructure.database.gateways.user import UserRepositoryImpl
from giveaway_bot.infrastructure.media_storage import MediaStorage


class GatewayProvider(Provider):
    scope = Scope.REQUEST
    user_repo = provide(provides=UserRepository, source=UserRepositoryImpl)
    media_repo = provide(provides=MediaRepository, source=MediaRepositoryImpl)

    @provide(scope=Scope.APP)
    def get_file_saver(self) -> MediaStorage:
        return MediaStorage(storage_path="./media")
