import pytest

import simaple.simulate.component.skill  # pylint: disable=W0611
from simaple.container.simulation import SimulationContainer
from simaple.container.memoizer import PersistentStorageMemoizer
from test_data.target import get_test_settings
from simaple.simulate.strategy.base import exec_by_strategy
import os


@pytest.mark.parametrize("environment_provider, jobtype, expected", get_test_settings())
def test_actor(environment_provider, jobtype, expected):
    environment = PersistentStorageMemoizer(os.path.join(os.path.dirname(__file__), ".memo.simaple.json")).compute_environment(
        environment_provider
    )
    container = SimulationContainer(environment)
    engine = container.operation_engine()

    policy = container.builtin_strategy().get_priority_based_policy()

    while engine.get_current_viewer()("clock") < 50_000:
        exec_by_strategy(engine, policy)

    report = list(engine.simulation_entries())

    """
    with open("operation.log", "w") as f:
        for op in engine.operation_logs():
            f.write(op.operation.expr+'\n')

    with open("history.log", "w") as f:
        for op in engine.operation_logs():
            for playlog in op.playlogs:
                f.write(f"{playlog.clock} | {playlog.action} | {playlog.events} \n")
    """

    dpm = container.damage_calculator().calculate_dpm(report)
    print(f"{engine.get_current_viewer()('clock')} | {jobtype} | {dpm:,} ")
    assert int(dpm) == expected
