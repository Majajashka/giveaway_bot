from dishka import Provider, Scope, provide

from giveaway_bot.application.interactors.giveaway.check_subscription import CheckSubscriptionInteractor
from giveaway_bot.application.interactors.giveaway.create_giveaway import CreateGiveawayInteractor
from giveaway_bot.application.interactors.giveaway.edit_giveawai_description import EditGiveawayDescriptionInteractor
from giveaway_bot.application.interactors.giveaway.edit_giveaway_step import EditGiveawayStepInteractor
from giveaway_bot.application.interactors.giveaway.edit_url import EditGiveawayIntegrationUrlInteractor
from giveaway_bot.application.interactors.giveaway.end_giveaway import EndGiveawayInteractor
from giveaway_bot.application.interactors.giveaway.extend_giveaway import ExtendGiveawayInteractor
from giveaway_bot.application.interactors.giveaway.get_active_giveaway import GetActiveGiveawayInteractor
from giveaway_bot.application.interactors.giveaway.get_all_active_giveaway import GetAllActiveGiveawayInteractor
from giveaway_bot.application.interactors.giveaway.get_giveaway_steps import GetGiveawayStepsInteractor
from giveaway_bot.application.interactors.giveaway.get_required_channel_links import GetRequiredChannelLinksInteractor
from giveaway_bot.application.interactors.giveaway.get_stats import GetGiveawayStartInteractor
from giveaway_bot.application.interactors.giveaway.hide_integration import HideIntegrationInteractor
from giveaway_bot.application.interactors.postback.change_subscription import EditSubscriptionInteractor
from giveaway_bot.application.interactors.postback.save_postback import SavePostbackInteractor
from giveaway_bot.application.interactors.user.get_or_create_user_interactor import GetOrCreateUserInteractor
from giveaway_bot.application.interactors.user.log_action import SaveUserActionInteractor


class InteractorProvider(Provider):
    scope = Scope.REQUEST

    get_or_create_user_interactor = provide(GetOrCreateUserInteractor)
    create_giveaway_interactor = provide(CreateGiveawayInteractor)
    get_giveaway_interactor = provide(GetActiveGiveawayInteractor)
    check_subscription_interactor = provide(CheckSubscriptionInteractor)
    get_channel_interactor = provide(GetRequiredChannelLinksInteractor)
    get_all_active_giveaways_interactor = provide(GetAllActiveGiveawayInteractor)
    extend_giveaway_interactor = provide(ExtendGiveawayInteractor)
    edit_giveaway_interactor = provide(EditGiveawayDescriptionInteractor)
    end_giveaway_interactor = provide(EndGiveawayInteractor)
    save_postback_interactor = provide(SavePostbackInteractor)
    get_giveaway_steps_interactor = provide(GetGiveawayStepsInteractor)
    edit_steps = provide(EditGiveawayStepInteractor)
    hide_integration = provide(HideIntegrationInteractor)
    change_url = provide(EditGiveawayIntegrationUrlInteractor)
    edit_subscription = provide(EditSubscriptionInteractor)
    save_user_interactor = provide(SaveUserActionInteractor)
    get_giveaway_stats = provide(GetGiveawayStartInteractor)