from typing import Any

import pydantic

from simaple.container.character_provider import (
    CharacterProvider,
    SimulationEnvironmentForCharacterProvider,
    get_character_provider,
)
from simaple.container.simulation import SimulationContainer, SimulationEnvironment


class _ProviderMetadata(pydantic.BaseModel):
    name: str
    data: dict[str, Any]
    environment: SimulationEnvironmentForCharacterProvider

    def get_character_provider_config(self) -> CharacterProvider:
        return get_character_provider(self.name, self.data)

    def get_simulation_environment(self) -> SimulationEnvironment:
        return self.get_character_provider_config().get_simulation_environment(
            self.environment,
        )


class PlanMetadata(pydantic.BaseModel):
    author: str = ""
    provider: _ProviderMetadata | None = None
    environment: SimulationEnvironment | None = None

    def get_character_provider_config(self) -> CharacterProvider:
        assert self.provider is not None
        return self.provider.get_character_provider_config()

    def load_container(self) -> SimulationContainer:
        if self.environment is None:
            assert self.provider is not None
            environment = self.provider.get_simulation_environment()
        else:
            environment = self.environment

        return SimulationContainer(environment)
