import pytest

import simaple.simulate.component.skill  # pylint: disable=W0611
from simaple.container.simulation import SimulationContainer
from simaple.simulate.report.base import Report, ReportEventHandler
from test_data.target import get_test_settings
from simaple.simulate.policy import get_dsl_shell


@pytest.mark.parametrize("setting, jobtype, expected", get_test_settings())
def test_actor(setting, jobtype, expected):
    container = SimulationContainer()
    container.config.from_dict(setting.model_dump())

    print(container.character().action_stat)

    client = container.client()
    policy = container.client_configuration().get_default_policy()

    report = Report()
    client.add_handler(ReportEventHandler(report))

    shell = get_dsl_shell(client)

    while client.show("clock") < 50_000:
        shell.exec_policy(policy, early_stop=50_000)

    dpm = container.dpm_calculator().calculate_dpm(report)
    print(f"{client.show('clock')} | {jobtype} | {dpm:,} ")
    assert int(dpm) == expected
