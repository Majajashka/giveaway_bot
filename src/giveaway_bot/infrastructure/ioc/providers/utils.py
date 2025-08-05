from dishka import provide, Provider, Scope

from giveaway_bot.application.interfaces.clock import Clock
from giveaway_bot.infrastructure.clock import ClockImpl


class UtilsProvider(Provider):
    scope = Scope.APP
    clock = provide(provides=Clock, source=ClockImpl)
