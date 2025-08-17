import logging

from aiogram import Router
from aiogram.types import CallbackQuery
from dishka import FromDishka

from giveaway_bot.application.interactors.giveaway.check_subscription import CheckSubscriptionInteractor
from giveaway_bot.application.interactors.giveaway.get_active_giveaway import GetActiveGiveawayInteractor
from giveaway_bot.application.interactors.giveaway.get_giveaway_steps import GetGiveawayStepsInteractor
from giveaway_bot.application.interactors.giveaway.get_required_channel_links import GetRequiredChannelLinksInteractor
from giveaway_bot.config import TelegramBotRequiredChannels, IntegrationConfig
from giveaway_bot.infrastructure.database.gateways.settings import SettingsRepo
from giveaway_bot.infrastructure.localization.translator import Localization
from giveaway_bot.infrastructure.media_storage import MediaStorage
from giveaway_bot.presentation.bot.keyboard.giveaway import ParticipateGiveawayCallbackData, build_links_keyboard, \
    CheckSubscriptionCallbackData, build_integration_keyboard
from giveaway_bot.presentation.bot.utils.integration import build_integration_url
from giveaway_bot.presentation.bot.utils.media import answer_by_media

router = Router()
logger = logging.getLogger(__name__)


@router.callback_query(ParticipateGiveawayCallbackData.filter())
async def participate_giveaway_handler(
        callback_query: CallbackQuery,
        callback_data: ParticipateGiveawayCallbackData,
        i18n: Localization,
        file_repo: FromDishka[MediaStorage],
        giveaway_interactor: FromDishka[GetGiveawayStepsInteractor],
        channel_links_interactor: FromDishka[GetRequiredChannelLinksInteractor]
):
    steps = await giveaway_interactor.execute(callback_data.giveaway_id)
    if not steps:
        await callback_query.message.answer(text=i18n("giveaway_not_found"))
        return
    step = steps.subscription_step

    links = await channel_links_interactor.execute()
    await callback_query.answer()
    await answer_by_media(
        event=callback_query,
        step=step,
        file_repo=file_repo,
        kb=build_links_keyboard(links=links, giveaway_id=steps.giveaway_id, buttons_per_row=1)
    )


@router.callback_query(CheckSubscriptionCallbackData.filter())
async def check_subscription_handler(
        callback_query: CallbackQuery,
        callback_data: CheckSubscriptionCallbackData,
        i18n: Localization,
        channel_links_interactor: FromDishka[CheckSubscriptionInteractor],
        file_repo: FromDishka[MediaStorage],
        giveaway_interactor: FromDishka[GetGiveawayStepsInteractor],
):
    steps = await giveaway_interactor.execute(callback_data.giveaway_id)
    if not steps:
        await callback_query.message.answer(text=i18n("giveaway_not_found"))
        return
    result = await channel_links_interactor.execute(user_id=callback_query.from_user.id)
    if result.is_fully_subscribed:
        await callback_query.message.delete_reply_markup()
        if steps.hide_integration:
            await answer_by_media(
                event=callback_query,
                step=steps.success_step,
                file_repo=file_repo
            )
            return
        else:
            await answer_by_media(
                event=callback_query,
                step=steps.integration_step,
                file_repo=file_repo,
                kb=build_integration_keyboard(url=steps.integration_url)
            )
            return
    elif result.not_subscribed_channels:
        await answer_by_media(
            event=callback_query,
            step=steps.subscription_step,
            file_repo=file_repo,
            kb=build_links_keyboard(links=result.not_subscribed_channels, giveaway_id=callback_data.giveaway_id,
                                    buttons_per_row=1)
        )
        return
