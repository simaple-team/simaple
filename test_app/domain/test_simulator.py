import pytest

from simaple.app.domain.simulator import Simulator


from simaple.simulate.base import Action


@pytest.mark.parametrize("index", [8, 10])
def test_simulator_rollback(sample_simulator: Simulator, index: int):
    for _ in range(10):
        sample_simulator.dispatch("ELAPSE 10.0")

    target_hash = sample_simulator.engine.history().get(index).hash
    
    sample_simulator.rollback(index)
    assert sample_simulator.engine.history().get(-1).hash == target_hash


@pytest.mark.parametrize("index", [8, 10])
def test_simulator_rollback_by_hash(sample_simulator: Simulator, index: int):
    for _ in range(10):
        sample_simulator.dispatch("ELAPSE 10.0")

    target_hash = sample_simulator.engine.history().get(index).hash

    sample_simulator.rollback_by_hash(target_hash)
    assert sample_simulator.engine.history().get(-1).hash == target_hash

