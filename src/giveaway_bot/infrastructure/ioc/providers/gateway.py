from dishka import Provider, Scope, provide

from giveaway_bot.application.interfaces.dao.giveaway import GiveawayRepository
from giveaway_bot.application.interfaces.dao.media import MediaRepository
from giveaway_bot.application.interfaces.dao.postback import PostbackRepository
from giveaway_bot.application.interfaces.dao.user import UserRepository
from giveaway_bot.infrastructure.database.gateways.giveaway import GiveawayRepoImpl
from giveaway_bot.infrastructure.database.gateways.media import MediaRepositoryImpl
from giveaway_bot.infrastructure.database.gateways.postback import PostbackRepoImpl
from giveaway_bot.infrastructure.database.gateways.user import UserRepositoryImpl
from giveaway_bot.infrastructure.media_storage import MediaStorage


class GatewayProvider(Provider):
    scope = Scope.REQUEST
    user_repo = provide(provides=UserRepository, source=UserRepositoryImpl)
    media_repo = provide(provides=MediaRepository, source=MediaRepositoryImpl)
    giveaway_repo = provide(provides=GiveawayRepository, source=GiveawayRepoImpl)
    postback_repo = provide(provides=PostbackRepository, source=PostbackRepoImpl)

    @provide(scope=Scope.APP)
    def get_file_saver(self) -> MediaStorage:
        return MediaStorage(storage_path="./media")
