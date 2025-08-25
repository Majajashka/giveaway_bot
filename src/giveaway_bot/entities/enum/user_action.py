from enum import StrEnum


class UserActionEnum(StrEnum):
    JOINED_GIVEAWAY = "joined_giveaway"
    SUBSCRIBED_TO_CHANNELS = "subscribed_to_channels"
    COMPLETED_REGISTRATION = "completed_registration"
    ACTIVATE_GIVEAWAY_SUBSCRIPTION = "activate_giveaway_subscription"
    DEACTIVATE_GIVEAWAY_SUBSCRIPTION = "deactivate_giveaway_subscription"