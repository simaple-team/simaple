from pathlib import Path

import pytest

import simaple.simulate.component.skill  # pylint: disable=W0611
from simaple.container.simulation import SimulationContainer, SimulationSetting
from simaple.core.job_category import JobCategory
from simaple.core.jobtype import JobType
from simaple.simulate.policy import get_dsl_shell
from simaple.simulate.report.base import Report, ReportEventHandler


@pytest.fixture(name="dsl_list")
def fixture_dsl_list() -> list[str]:
    with open(Path(__file__).parent / "archmage_tc_runtime.txt", encoding="utf-8") as f:
        dsl_list = [line.strip() for line in f.readlines()]

    return dsl_list


@pytest.fixture(name="dsl_test_setting")
def fixture_dsl_test_setting():
    cache_dir = str(Path(__file__).parent)

    return SimulationSetting(
        tier="Legendary",
        jobtype=JobType.archmagetc,
        job_category=JobCategory.magician,
        level=270,
        passive_skill_level=0,
        combat_orders_level=1,
        v_skill_level=30,
        v_improvements_level=60,
        cache_root_dir=cache_dir,
    )


def test_dsl(dsl_list: list[str], dsl_test_setting: SimulationSetting) -> None:
    container = SimulationContainer()
    container.config.from_pydantic(dsl_test_setting)

    test_client = container.client()
    environment = test_client.environment

    report = Report()
    test_client.add_handler(ReportEventHandler(report))
    shell = get_dsl_shell(test_client)

    for dsl in dsl_list:
        shell.exec_dsl(dsl)

    print(
        f"{environment.show('clock')} | {container.dpm_calculator().calculate_dpm(report):,} "
    )
    assert 6534916107988.739 == container.dpm_calculator().calculate_dpm(report)
