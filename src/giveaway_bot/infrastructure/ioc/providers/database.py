from collections.abc import AsyncIterable

from dishka import Provider, Scope, provide
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from giveaway_bot.application.interfaces.uow import UoW
from giveaway_bot.config import PostgresqlConfig, RedisConfig
from giveaway_bot.infrastructure.database.uow import SqlalchemyUoW


class DatabaseProvider(Provider):
    scope = Scope.APP

    @provide
    async def get_async_engine(
        self, db_config: PostgresqlConfig,
    ) -> AsyncIterable[AsyncEngine]:
        engine = create_async_engine(
            url=db_config.get_database_url(), pool_size=25, max_overflow=15, pool_timeout=300,
        )
        yield engine
        await engine.dispose(close=True)

    @provide
    def get_sessionmaker(self, engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
        return async_sessionmaker(engine)

    @provide(scope=Scope.REQUEST)
    async def get_session(
        self, sessionmaker: async_sessionmaker[AsyncSession],
    ) -> AsyncIterable[AsyncSession]:
        session = sessionmaker()
        try:
            yield session
        finally:
            await session.close()

    @provide
    async def get_redis(self, config: RedisConfig) -> Redis:
        return Redis(host=config.REDIS_HOST, port=config.REDIS_PORT)

    @provide(scope=Scope.REQUEST)
    async def get_uow(self, session: AsyncSession) -> UoW:
        return SqlalchemyUoW(session)

