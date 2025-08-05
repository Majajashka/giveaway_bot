from datetime import datetime, UTC
from typing import Protocol


class Clock(Protocol):

    def now(self) -> datetime:
        raise NotImplementedError
