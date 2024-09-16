import pytest

from simaple.app.domain.simulator import Simulator

from simaple.container.character_provider import MinimalCharacterProvider
from simaple.container.simulation import SimulationSetting


@pytest.fixture
def sample_simulator(simulator_configuration):
    return Simulator.create_from_config(
        simulation_setting=SimulationSetting()
        ,character_provider=MinimalCharacterProvider.model_validate(simulator_configuration)
    )
