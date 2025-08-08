from giveaway_bot.application.interfaces.subscription import ChannelLinkService
from giveaway_bot.config import TelegramBotRequiredChannels


class GetRequiredChannelLinksInteractor:

    def __init__(self, link_service: ChannelLinkService, config: TelegramBotRequiredChannels):
        self.link_service = link_service
        self._config = config

    async def execute(self):
        """
        Returns a list of channel links required for the giveaway.
        """
        return [
            await self.link_service.get_link(channel_id)
            for channel_id in self._config.channels
        ]
