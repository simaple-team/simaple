import pytest

from simaple.app.domain.simulator import Simulator
from simaple.app.domain.simulator_configuration import MinimalSimulatorConfiguration


from simaple.simulate.base import Action


@pytest.mark.parametrize("index", [8, 10])
def test_simulator_rollback(sample_simulator: Simulator, index: int):
    for _ in range(10):
        sample_simulator.dispatch(Action(
            name="*",
            method="elapse",
            payload=10.0,
        ))

    target_hash = sample_simulator.history.get(index).hash
    
    sample_simulator.rollback(index)
    assert sample_simulator.history.get_latest_playlog().hash == target_hash


@pytest.mark.parametrize("index", [8, 10])
def test_simulator_rollback_by_hash(sample_simulator: Simulator, index: int):
    for _ in range(10):
        sample_simulator.dispatch(Action(
            name="*",
            method="elapse",
            payload=10.0,
        ))

    target_hash = sample_simulator.history.get(index).hash

    sample_simulator.rollback_by_hash(target_hash)
    assert sample_simulator.history.get_latest_playlog().hash == target_hash

