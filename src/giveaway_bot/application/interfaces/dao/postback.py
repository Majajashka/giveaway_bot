from typing import Protocol


class PostbackRepository(Protocol):
    async def save(self, tg_id: int, data: dict) -> None:
        """Save postback data and return its ID."""
        raise NotImplementedError
