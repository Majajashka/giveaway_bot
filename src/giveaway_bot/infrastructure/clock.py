from datetime import UTC, datetime

from giveaway_bot.application.interfaces.clock import Clock


class ClockImpl(Clock):

    def now(self) -> datetime:
        return datetime.now()
