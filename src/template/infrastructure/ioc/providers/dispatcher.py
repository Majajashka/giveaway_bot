import logging

from aiogram import Dispatcher
from aiogram.fsm.storage.base import BaseEventIsolation, BaseStorage, DefaultKeyBuilder
from aiogram.fsm.storage.memory import MemoryStorage, SimpleEventIsolation
from aiogram.fsm.storage.redis import RedisEventIsolation, RedisStorage
from dishka import Provider, Scope, provide
from redis.asyncio import Redis

from template.config import TelegramBotConfig, TelegramBotStorageType
from template.presentation.bot.handlers import get_router
from template.presentation.bot.middlewares import setup_middlewares

logger = logging.getLogger(__name__)


class DpProvider(Provider):
    scope = Scope.APP

    @provide
    async def get_dp(self, storage: BaseStorage, isolation: BaseEventIsolation) -> Dispatcher:
        dp = Dispatcher(storage=storage, events_isolation=isolation)
        logger.info("Including routers to main dispatcher...")
        dp.include_router(get_router())
        logger.info("Setting up middlewares to main dispatcher...")
        setup_middlewares(dp)
        return dp

    @provide
    async def get_storage(self, config: TelegramBotConfig, redis: Redis) -> BaseStorage:
        if config.storage.storage_type == TelegramBotStorageType:
            return RedisStorage(
                redis=redis,
                key_builder=DefaultKeyBuilder(with_bot_id=True, with_destiny=True),
            )
        else:
            return MemoryStorage()

    @provide
    async def get_event_isolation(self, config: TelegramBotConfig, redis: Redis) -> BaseEventIsolation:
        if config.storage.storage_type == TelegramBotStorageType.REDIS:
            return RedisEventIsolation(
                redis=redis,
                key_builder=DefaultKeyBuilder(with_bot_id=True, with_destiny=True),
            )
        else:
            return SimpleEventIsolation()
