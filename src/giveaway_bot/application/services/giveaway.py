import logging
import re
import uuid
from dataclasses import dataclass
from uuid import UUID

from giveaway_bot.application.interfaces.dao.giveaway import GiveawayRepository
from giveaway_bot.config import IntegrationConfig
from giveaway_bot.entities.domain.giveaway import GiveawayStep

logger = logging.getLogger(__name__)


@dataclass
class  GiveawaySteps:
    giveaway_id: UUID
    hide_integration: bool
    integration_url: str
    description_step: GiveawayStep
    subscription_step: GiveawayStep
    integration_step: GiveawayStep
    success_step: GiveawayStep


class GiveawayService:

    def __init__(self, giveaway_repository: GiveawayRepository, integration_config: IntegrationConfig):
        self._giveaway_repo = giveaway_repository
        self._integration_config = integration_config

    async def get_giveaway_steps(self, giveaway_id: UUID, user_id: int) -> GiveawaySteps | None:
        """
        Get all steps of a giveaway by its ID.

        :param giveaway_id: ID of the giveaway.
        :return: List of step IDs.
        """
        default_dialogue = await self._giveaway_repo.get_default_dialog()
        current_dialogue = await self._giveaway_repo.get_by_id(giveaway_id)
        if not current_dialogue:
            logger.warning("Giveaway with ID %s not found for steps.", giveaway_id)
            return None
        description_step = current_dialogue.description_step if current_dialogue.description_step else default_dialogue.description_step
        subscription_step = current_dialogue.subscription_step if current_dialogue.subscription_step else default_dialogue.subscription_step
        integration_step = current_dialogue.integration_step if current_dialogue.integration_step else default_dialogue.integration_step
        success_step = current_dialogue.success_step if current_dialogue.success_step else default_dialogue.success_step
        link = f"{current_dialogue.integration_url}?sub1={user_id}&sub2={giveaway_id}&cid={uuid.uuid4()}"
        integration_step.text = re.sub(
            r'(<a\s+[^>]*href=")([^"]*)(")',
            rf'\1{link}\3',
            integration_step.text
        )
        if "{link}" in integration_step.text:
            integration_step.text = integration_step.text.format(link=link)
        return GiveawaySteps(
            giveaway_id=giveaway_id,
            description_step=description_step,
            subscription_step=subscription_step,
            integration_step=integration_step,
            success_step=success_step,
            hide_integration=current_dialogue.hide_integration,
            integration_url=link
        )
