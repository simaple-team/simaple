from typing import Any

import pydantic

from simaple.app.domain.simulator import Simulator
from simaple.container.character_provider import get_character_provider
from simaple.container.simulation import CharacterProvider, SimulationSetting
from simaple.container.simulation import (
    CharacterProvider,
    SimulationContainer,
    SimulationSetting,
)


class PlanMetadata(pydantic.BaseModel):
    configuration_name: str
    author: str = ""
    data: dict[str, Any]
    simulation_setting: SimulationSetting

    def get_character_provider_config(self) -> CharacterProvider:
        return get_character_provider(self.configuration_name, self.data)

    def load_simulator(self) -> SimulationContainer:
        container = SimulationContainer(
            setting=self.simulation_setting,
            character_provider=self.get_character_provider_config(),
        )
        return container
