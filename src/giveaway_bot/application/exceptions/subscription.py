from giveaway_bot.application.exceptions.base import ApplicationError


class BotNotInChannelError(ApplicationError):
    """Exception raised when the bot is not in the channel."""

    def __init__(self, channel_id: int):
        super().__init__(f"The bot is not in the channel: {channel_id}")
        self.channel_id = channel_id
