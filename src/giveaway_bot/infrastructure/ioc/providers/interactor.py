from dishka import Provider, Scope, provide

from giveaway_bot.application.interactors.giveaway.create_giveaway import CreateGiveawayInteractor
from giveaway_bot.application.interactors.giveaway.get_active_giveaway import GetActiveGiveawayInteractor
from giveaway_bot.application.interactors.user.get_or_create_user_interactor import GetOrCreateUserInteractor


class InteractorProvider(Provider):
    scope = Scope.REQUEST

    get_or_create_user_interactor = provide(GetOrCreateUserInteractor)
    create_giveaway_interactor = provide(CreateGiveawayInteractor)
    get_giveaway_interactor = provide(GetActiveGiveawayInteractor)