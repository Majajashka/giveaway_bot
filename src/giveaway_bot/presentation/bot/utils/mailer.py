import asyncio
import logging
from dataclasses import dataclass
from io import BytesIO
from typing import Optional, Iterable

from aiogram import Bot
from aiogram.exceptions import TelegramRetryAfter
from aiogram.types import InlineKeyboardMarkup, InputMediaPhoto, BufferedInputFile

logger = logging.getLogger(__name__)


@dataclass
class MailingResult:
    success: int = 0
    failed: int = 0

    def __add__(self, other):
        if isinstance(other, MailingResult):
            return MailingResult(
                self.success + other.success, self.failed + other.failed
            )
        return NotImplemented

    def __iadd__(self, other):
        if isinstance(other, MailingResult):
            self.success += other.success
            self.failed += other.failed
            return self
        return NotImplemented

    @property
    def total(self) -> int:
        return self.success + self.failed


@dataclass
class MailingTaskDTO:
    bot_id: int
    chat_id: int
    message: str
    media: Optional[bytes] = None
    keyboard_markup: Optional[InlineKeyboardMarkup] = None


class TGNotificator:
    def __init__(self, bot: Bot, batch_size: int = 25, send_interval: float = 1):
        self.bot = bot
        self.batch_size = batch_size
        self.send_interval = send_interval

    async def send_notifications(self, user_messages: Iterable[MailingTaskDTO]) -> MailingResult:
        mailing_result = MailingResult()
        batch = []

        for msg in user_messages:
            batch.append(msg)
            if len(batch) == self.batch_size:
                mailing_result += await self._send_messages(batch)
                batch.clear()
                await asyncio.sleep(self.send_interval)

        if batch:
            mailing_result += await self._send_messages(batch)

        return mailing_result

    async def _send_messages(self, user_messages: list[MailingTaskDTO]) -> MailingResult:
        mailing_result = MailingResult()
        tasks = []

        for msg in user_messages:
            if msg.media:
                tasks.append(
                    self.bot.send_photo(
                        chat_id=msg.chat_id,
                        photo=BufferedInputFile(msg.media, filename="photo.jpg"),
                        caption=msg.message,
                        reply_markup=msg.keyboard_markup,
                    )
                )
            else:
                tasks.append(
                    self.bot.send_message(
                        chat_id=msg.chat_id,
                        text=msg.message,
                        reply_markup=msg.keyboard_markup,
                    )
                )

        results = await asyncio.gather(*tasks, return_exceptions=True)

        for res in results:
            if isinstance(res, TelegramRetryAfter):
                logger.warning(f"Rate limit exceeded: {res}")
            elif isinstance(res, Exception):
                mailing_result.failed += 1
                logger.error(f"Send error: {res}")
            else:
                mailing_result.success += 1

        return mailing_result

    async def send_notification(self, user_message: MailingTaskDTO) -> MailingResult:
        return await self._send_messages([user_message])
