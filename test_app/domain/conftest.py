import pytest

from simaple.app.domain.simulator import Simulator
from simaple.simulate.interface.simulator_configuration import MinimalSimulatorConfiguration


@pytest.fixture(name="minimal_simulator_configuration")
def fixture_minimal_simulator_configuration(simulator_configuration):
    return MinimalSimulatorConfiguration.model_validate(simulator_configuration)


@pytest.fixture
def sample_simulator(minimal_simulator_configuration):
    return Simulator.create_from_config(minimal_simulator_configuration)
