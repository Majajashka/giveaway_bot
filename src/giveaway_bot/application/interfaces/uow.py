from typing import Protocol


class UoW(Protocol):

    async def commit(self) -> None:
        """Commit the transaction."""
        raise NotImplementedError

    async def rollback(self) -> None:
        """Rollback the transaction."""
        raise NotImplementedError

    async def flush(self) -> None:
        """Flush the session."""
        raise NotImplementedError
