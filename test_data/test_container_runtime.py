import pytest

import simaple.simulate.component.skill  # pylint: disable=W0611
from simaple.container.simulation import SimulationContainer
from simaple.simulate.report.base import Report, ReportEventHandler
from test_data.target import get_test_settings
from simaple.simulate.policy.base import get_interpreter


@pytest.mark.parametrize("setting, jobtype, expected", get_test_settings())
def test_actor(setting, jobtype, expected):
    container = SimulationContainer()
    container.config.from_pydantic(setting)

    print(container.character().action_stat)

    client = container.client()
    policy = container.client_configuration().get_default_policy()

    environment = client.environment

    report = Report()
    client.add_handler(ReportEventHandler(report))

    interpreter = get_interpreter(client)

    while environment.show("clock") < 50_000:
        interpreter.exec_policy(policy, early_stop=50_000)

    dpm = container.dpm_calculator().calculate_dpm(report)
    print(f"{environment.show('clock')} | {jobtype} | {dpm:,} ")
    assert int(dpm) == expected
