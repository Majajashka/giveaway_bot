from dishka import Provider, Scope, provide

from giveaway_bot.application.interfaces.subscription import SubscriptionChecker, ChannelLinkService
from giveaway_bot.application.services.giveaway import GiveawayService
from giveaway_bot.application.services.subcription import SubscriptionCheckService
from giveaway_bot.config import TelegramBotConfig
from giveaway_bot.infrastructure.aiogram.subscription import ChannelLinkServiceImpl


class ServiceProvider(Provider):
    scope = Scope.REQUEST

    sub_checker_service = provide(SubscriptionCheckService)
    channel_service = provide(provides=ChannelLinkService, source=ChannelLinkServiceImpl)
    giveaway_service = provide(provides=GiveawayService, source=GiveawayService, scope=Scope.REQUEST)

    @provide
    def get_subscription_check_service(
            self,
            config: TelegramBotConfig,
            checker: SubscriptionChecker
    ) -> SubscriptionCheckService:
        return SubscriptionCheckService(
            checker=checker,
            required_channels=config.required_channels.channels
        )
