from typing import Protocol


class SubscriptionChecker(Protocol):

    async def is_subscribed(self, tg_id: int, channel_id: int) -> bool:
        """Check if the user is subscribed to the channel."""
        raise NotImplementedError


class ChannelLinkService(Protocol):
    async def get_link(self, channel_id: int) -> str:
        """Get the link to the channel."""
        raise NotImplementedError