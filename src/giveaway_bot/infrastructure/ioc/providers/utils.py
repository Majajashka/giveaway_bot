from dishka import Provider, Scope, provide

from giveaway_bot.application.interfaces.clock import Clock
from giveaway_bot.application.interfaces.subscription import SubscriptionChecker
from giveaway_bot.infrastructure.aiogram.subscription import SubscriptionCheckerImpl
from giveaway_bot.infrastructure.clock import ClockImpl


class UtilsProvider(Provider):
    scope = Scope.APP
    clock = provide(provides=Clock, source=ClockImpl)
    subscription_checker = provide(provides=SubscriptionChecker, source=SubscriptionCheckerImpl)

