from typing import Any

import pydantic

from simaple.container.character_provider import (
    CharacterProvider,
    SimulationEnvironmentForCharacterProvider,
    get_character_provider,
)
from simaple.container.simulation import SimulationContainer


class _ProviderMetadata(pydantic.BaseModel):
    configuration_name: str
    data: dict[str, Any]
    simulation_environment: SimulationEnvironmentForCharacterProvider


class PlanMetadata(pydantic.BaseModel):
    author: str = ""
    provider: _ProviderMetadata

    def get_character_provider_config(self) -> CharacterProvider:
        return get_character_provider(self.configuration_name, self.data)

    def load_container(self) -> SimulationContainer:
        return self.get_character_provider_config().get_simulation_container(
            self.simulation_environment,
        )
