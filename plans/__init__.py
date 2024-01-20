import pytest

import simaple.simulate.component.skill  # pylint: disable=W0611
from simaple.container.simulation import SimulationContainer
from test_data.target import get_test_settings


@pytest.mark.parametrize("setting, jobtype, expected", get_test_settings())
def test_actor(setting, jobtype, expected):
    container = SimulationContainer()
    container.config.from_dict(setting.model_dump())

    print(container.character().action_stat)

    engine = container.operation_engine()

    policy = container.engine_configuration().get_default_policy()

    while engine.get_current_viewer()("clock") < 50_000:
        engine.exec_policy(policy, early_stop=50_000)

    report = engine.create_full_report()

    dpm = container.dpm_calculator().calculate_dpm(report)
    print(f"{engine.get_current_viewer()('clock')} | {jobtype} | {dpm:,} ")
    assert int(dpm) == expected
