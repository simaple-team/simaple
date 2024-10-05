from typing import Any, Type

import pydantic

from simaple.container.api_environment_provider import NexonAPIEnvironmentProvider
from simaple.container.environment_provider import (
    BaselineEnvironmentProvider,
    EnvironmentProvider,
    MinimalEnvironmentProvider,
)
from simaple.container.simulation import SimulationEnvironment

_environment_providers: dict[str, Type[EnvironmentProvider]] = {
    BaselineEnvironmentProvider.__name__: BaselineEnvironmentProvider,
    MinimalEnvironmentProvider.__name__: MinimalEnvironmentProvider,
    NexonAPIEnvironmentProvider.__name__: NexonAPIEnvironmentProvider,
}


def get_environment_provider(name: str, config: dict) -> EnvironmentProvider:
    return _environment_providers[name].model_validate(config)


class _ProviderMetadata(pydantic.BaseModel):
    name: str
    data: dict[str, Any]

    def get_environment_provider(self) -> EnvironmentProvider:
        return get_environment_provider(self.name, self.data)

    def get_simulation_environment(self) -> SimulationEnvironment:
        return self.get_environment_provider().get_simulation_environment()


class PlanMetadata(pydantic.BaseModel):
    author: str = ""
    provider: _ProviderMetadata | None = None
    environment: SimulationEnvironment | None = None

    def get_environment_provider_config(self) -> EnvironmentProvider:
        assert self.provider is not None
        return self.provider.get_environment_provider()

    def get_environment(self) -> SimulationEnvironment:
        if self.environment is None:
            assert self.provider is not None
            environment = self.provider.get_simulation_environment()
        else:
            environment = self.environment

        return environment
