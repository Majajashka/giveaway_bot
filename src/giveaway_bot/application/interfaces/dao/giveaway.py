from datetime import datetime
from typing import Protocol, Literal
from uuid import UUID

from giveaway_bot.application.dtos.giveaway import CreateGiveawayDTO, CreateGiveawayStepDTO
from giveaway_bot.entities.domain.giveaway import Giveaway, GiveawayStep


class GiveawayRepository(Protocol):

    async def create(self, giveaway_data: CreateGiveawayDTO) -> Giveaway:
        """Create a new giveaway."""
        raise NotImplementedError

    async def get_by_id(self, giveaway_id: UUID) -> Giveaway | None:
        """Get a giveaway by its ID."""
        raise NotImplementedError

    async def get_all(self, active_only: bool = False) -> list[Giveaway]:
        """Get all giveaways, optionally filtering by active status."""
        raise NotImplementedError

    async def update_step(
            self,
            giveaway_id: UUID,
            step_type: Literal["description", "subscription", "integration", "success"],
            step_data: CreateGiveawayStepDTO,
    ) -> None:
        """
        Update a specific step of a giveaway.

        :param giveaway_id: ID of the giveaway.
        :param step_type: Type of the step to update (description, subscription, integration, success).
        :param step_data: Data for the step.
        """
        raise NotImplementedError

    async def edit_giveaway_date(
        self,
        giveaway_id: UUID,
        new_date: datetime
    ) -> None:
        """Edit the date of an existing giveaway."""
        raise NotImplementedError

    async def get_default_dialog(self) -> Giveaway:
        """Get the default dialog for giveaways."""
        raise NotImplementedError

    async def change_giveaway_hide_integration(self, giveaway_id: UUID) -> None:
        raise NotImplementedError

    async def edit_integration_url(self, giveaway_id: UUID, url: str) -> None:
        raise NotImplementedError

