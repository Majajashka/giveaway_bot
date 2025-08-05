from dishka import Provider, Scope, provide

from giveaway_bot.application.interactors.user.get_or_create_user_interactor import GetOrCreateUserInteractor


class InteractorProvider(Provider):
    scope = Scope.REQUEST

    get_or_create_user_interactor = provide(GetOrCreateUserInteractor)
