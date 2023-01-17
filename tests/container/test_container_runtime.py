import pytest

import simaple.simulate.component.skill  # pylint: disable=W0611
from simaple.container.simulation import SimulationContainer
from simaple.simulate.report.base import Report, ReportEventHandler
from tests.container.target import get_test_settings


@pytest.mark.parametrize("setting, jobtype, expected", get_test_settings())
def test_actor(setting, jobtype, expected):
    container = SimulationContainer()
    container.config.from_pydantic(setting)

    client = container.client()
    actor = container.client_configuration().get_mdc_actor()

    environment = client.environment

    report = Report()
    client.add_handler(ReportEventHandler(report))

    events = []
    while environment.show("clock") < 50_000:
        action = actor.decide(environment, events)
        events = client.play(action)

    dpm = container.dpm_calculator().calculate_dpm(report)
    print(f"{environment.show('clock')} | {jobtype} | {dpm:,} ")
    assert int(dpm) == expected
