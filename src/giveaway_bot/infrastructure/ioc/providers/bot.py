from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import User
from dishka import Provider, Scope, from_context, provide

from giveaway_bot.config import LocalizationConfig, TelegramBotConfig, TelegramBotOwnerConfig
from giveaway_bot.infrastructure.localization.translator import LocalizationStorage, build_localization_storage
from giveaway_bot.presentation.bot.utils.clock import LocalizedClock


class BotProvider(Provider):
    scope = Scope.APP

    user = from_context(User, scope=Scope.REQUEST)

    @provide
    async def get_bot(self, config: TelegramBotConfig) -> Bot:
        return Bot(
            token=config.token,
            default=DefaultBotProperties(
                parse_mode=ParseMode.HTML,
                link_preview_is_disabled=True,
            ),
        )

    @provide
    def get_localized_clock(self, config: TelegramBotOwnerConfig) -> LocalizedClock:
        return LocalizedClock(timezone=config.timezone)


class LocalizationProvider(Provider):
    scope = Scope.APP

    @provide
    def get_localization_storage(self, config: LocalizationConfig) -> LocalizationStorage:
        """
        Returns the localization string for the bot.
        This can be used to set the locale for the bot.
        """
        return build_localization_storage(config)
