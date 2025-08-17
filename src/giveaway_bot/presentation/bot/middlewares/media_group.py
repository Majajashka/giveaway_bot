import asyncio
import logging
import time
from typing import Callable, Any, Awaitable, Optional

from aiogram import BaseMiddleware, Router
from aiogram.types import Message
from aiogram_album import AlbumMessage
from cachetools import TTLCache

logger = logging.getLogger(__name__)
class LockAlbumMiddleware(BaseMiddleware):
    def __init__(self, latency=0.2, maxsize=1000, ttl=10, router=None):
        self.latency = latency
        self.cache = TTLCache(maxsize=maxsize, ttl=ttl + 20)
        self.locks: dict[tuple[int, str], asyncio.Lock] = {}
        if router:
            router.message.outer_middleware(self)
            router.channel_post.outer_middleware(self)

    async def __call__(
            self,
            handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: dict[str, Any],
    ) -> Any:
        if event.media_group_id is None:
            return await handler(event, data)

        key = (event.chat.id, event.media_group_id)
        if key not in self.locks:
            self.locks[key] = asyncio.Lock()

        async with self.locks[key]:
            self.cache.setdefault(key, [])
            if event not in self.cache[key]:
                self.cache[key].append(event)

            await asyncio.sleep(self.latency)

            smallest_id = min(m.message_id for m in self.cache[key])
            if event.message_id != smallest_id:
                return

            album_messages = self.cache.pop(key)
            self.locks.pop(key, None)  # очистить лок

        album = AlbumMessage.new(messages=album_messages, data=data)
        return await handler(album, data)


class DebugAlbumMiddleware(BaseMiddleware):
    def __init__(
        self,
        latency: int | float = 0.2,
        router: Optional[Router] = None,
    ):
        self.latency = latency
        self.cache: dict[str, list[Message]] = {}
        self.first_msg_time: dict[str, float] = {}
        if router:
            router.message.outer_middleware(self)
            router.channel_post.outer_middleware(self)

    async def __call__(
        self,
        handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: dict[str, Any],
    ) -> Any:
        media_group_id = event.media_group_id
        chat_id = event.chat.id if event.chat else "no_chat"

        # Если нет media_group_id, просто вызываем обработчик
        if not media_group_id:
            logger.debug(f"[No Album] chat_id={chat_id} message_id={event.message_id} update_id={event.update.update_id}")
            return await handler(event, data)

        key = f"{chat_id}:{media_group_id}"
        now = time.monotonic()

        if key not in self.cache:
            self.cache[key] = []
            self.first_msg_time[key] = now
            logger.debug(f"[First message] key={key} at {now:.3f}")

        self.cache[key].append(event)
        logger.debug(f"[Add message] key={key} message_id={event.message_id} total_messages={len(self.cache[key])} elapsed={now - self.first_msg_time[key]:.3f}s")

        # Ждем немного, чтобы собрать все сообщения альбома
        logger.debug(f"[Sleep] Waiting {self.latency}s to collect album messages for key={key}")
        await asyncio.sleep(self.latency)

        total_messages_after_sleep = len(self.cache.get(key, []))
        logger.debug(f"[After sleep] key={key} collected_messages={total_messages_after_sleep}")

        # Если за это время пришло больше сообщений — выходим, ждем следующего вызова
        if total_messages_after_sleep > len(self.cache[key]):
            logger.debug(f"[Not ready] key={key} more messages arrived, waiting for next call")
            return

        album_messages = self.cache.pop(key, [])
        self.first_msg_time.pop(key, None)
        logger.debug(f"[Handle album] key={key} total_messages={len(album_messages)}")

        album_event = AlbumMessage.new(messages=album_messages, data=data)

        try:
            result = await handler(album_event, data)
            logger.debug(f"[Handled album] key={key} successfully processed")
            return result
        except Exception as e:
            logger.exception(f"[Error handling album] key={key} error: {e}")
            raise