from typing import Any

import pydantic

from simaple.container.character_provider import get_character_provider
from simaple.container.simulation import (
    CharacterProvider,
    SimulationContainer,
    SimulationEnvironment,
)


class PlanMetadata(pydantic.BaseModel):
    configuration_name: str
    author: str = ""
    data: dict[str, Any]
    simulation_environment: SimulationEnvironment

    def get_character_provider_config(self) -> CharacterProvider:
        return get_character_provider(self.configuration_name, self.data)

    def load_container(self) -> SimulationContainer:
        container = SimulationContainer.from_character_provider(
            self.simulation_environment,
            self.get_character_provider_config(),
        )
        return container
