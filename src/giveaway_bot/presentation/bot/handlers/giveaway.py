import logging

from aiogram import Router
from aiogram.types import CallbackQuery
from dishka import FromDishka

from giveaway_bot.application.interactors.giveaway.check_subscription import CheckSubscriptionInteractor
from giveaway_bot.application.interactors.giveaway.get_active_giveaway import GetActiveGiveawayInteractor
from giveaway_bot.application.interactors.giveaway.get_required_channel_links import GetRequiredChannelLinksInteractor
from giveaway_bot.config import TelegramBotRequiredChannels, IntegrationConfig
from giveaway_bot.infrastructure.localization.translator import Localization
from giveaway_bot.presentation.bot.keyboard.giveaway import ParticipateGiveawayCallbackData, build_links_keyboard, \
    CheckSubscriptionCallbackData
from giveaway_bot.presentation.bot.utils.integration import build_integration_url

router = Router()
logger = logging.getLogger(__name__)


@router.callback_query(ParticipateGiveawayCallbackData.filter())
async def participate_giveaway_handler(
        callback_query: CallbackQuery,
        callback_data: ParticipateGiveawayCallbackData,
        i18n: Localization,
        giveaway_interactor: FromDishka[GetActiveGiveawayInteractor],
        channel_links_interactor: FromDishka[GetRequiredChannelLinksInteractor]
):
    giveaway = await giveaway_interactor.execute(callback_data.giveaway_id)
    if not giveaway:
        await callback_query.message.answer(text=i18n("giveaway_not_found"))
        return

    links = await channel_links_interactor.execute()
    await callback_query.answer()
    await callback_query.message.answer(
        text=i18n("giveaway-instructions"),
        reply_markup=build_links_keyboard(links=links, giveaway_id=giveaway.id, buttons_per_row=1)
    )


@router.callback_query(CheckSubscriptionCallbackData.filter())
async def check_subscription_handler(
        callback_query: CallbackQuery,
        callback_data: CheckSubscriptionCallbackData,
        i18n: Localization,
        channel_links_interactor: FromDishka[CheckSubscriptionInteractor],
        config: FromDishka[IntegrationConfig]
):
    result = await channel_links_interactor.execute(user_id=callback_query.from_user.id)
    if result.is_fully_subscribed:
        await callback_query.message.delete_reply_markup()
        await callback_query.message.edit_text(
            text=i18n(
                "giveaway-after-subscription-instructions",
                link=build_integration_url(
                    url=config.service_url,
                    user_id=callback_query.from_user.id,
                ),
            )
        )
        return
    elif result.not_subscribed_channels:
        await callback_query.message.edit_text(
            text=i18n("giveaway-subscription-not-subscribed"),
            reply_markup=build_links_keyboard(links=result.not_subscribed_channels, giveaway_id=callback_data.giveaway_id, buttons_per_row=1)
        )
        return
