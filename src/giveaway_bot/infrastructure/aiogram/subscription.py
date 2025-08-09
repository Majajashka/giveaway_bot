import logging

from aiogram import Bot
from aiogram.enums import ChatMemberStatus
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from redis.asyncio import Redis

from giveaway_bot.application.exceptions.subscription import BotNotInChannelError
from giveaway_bot.application.interfaces.subscription import SubscriptionChecker, ChannelLinkService
from giveaway_bot.config import TelegramBotOwnerConfig

logger = logging.getLogger(__name__)


class SubscriptionCheckerImpl(SubscriptionChecker):

    def __init__(self, bot: Bot):
        self._bot = bot

    async def is_subscribed(self, tg_id: int, channel_id: int) -> bool:
        try:
            member = await self._bot.get_chat_member(self._format_channel_id(channel_id), tg_id)
        except (TelegramBadRequest, TelegramForbiddenError) as e:
            logger.warning(e)
            raise BotNotInChannelError(channel_id=channel_id) from e
        return member.status not in (ChatMemberStatus.LEFT, ChatMemberStatus.KICKED)

    @staticmethod
    def _format_channel_id(channel_id: int) -> int:
        if not str(channel_id).startswith("-100"):
            return int(f'-100{channel_id}')
        return channel_id


class ChannelLinkServiceImpl(ChannelLinkService):
    def __init__(self, bot: Bot, redis: Redis, config: TelegramBotOwnerConfig):
        self.bot = bot
        self.redis = redis
        self._owner_config = config

    async def get_link(self, channel_id: int) -> str:
        cache_key = f"channel_username:{channel_id}"
        username = await self.redis.get(cache_key)
        logger.info(type(channel_id))

        if username:
            logger.debug(f"Cache hit for channel {channel_id}: {username}")
            return f"https://t.me/{username.decode()}"
        try:
            chat = await self.bot.get_chat(self._format_channel_id(channel_id))
            logger.info(chat)
        except (TelegramBadRequest, TelegramForbiddenError) as e:
            logger.error(f"Failed to get chat for channel {channel_id}: {e}")
            link = self.make_channel_link(channel_id)
            await self.bot.send_message(
                chat_id=self._owner_config.tg_user_id,
                text=(
                    f'Не удалось получить информацию о канале <a href="{link}">{channel_id}</a>. '
                    "Убедитесь, что бот является администратором канала."
                )
            )
            raise ValueError(f"Invalid channel ID: {channel_id}") from e
        if not chat.username:
            raise ValueError(f"Channel {channel_id} has no username")

        await self.redis.set(cache_key, chat.username, ex=60 * 15)
        return f"https://t.me/{chat.username}"

    @staticmethod
    def make_channel_link(channel_id: int) -> str:
        if str(channel_id).startswith("-100"):
            trimmed_id = str(channel_id)[4:]
        else:
            trimmed_id = str(channel_id).lstrip("-")

        return f"https://t.me/c/{trimmed_id}"

    @staticmethod
    def _format_channel_id(channel_id: int) -> int:
        if not str(channel_id).startswith("-100"):
            return int(f'-100{channel_id}')
        return channel_id
