import os
from pathlib import Path

import pytest

import simaple.simulate.component.skill  # noqa: F401
from simaple.container.environment_provider import BaselineEnvironmentProvider
from simaple.container.memoizer import PersistentStorageMemoizer
from simaple.container.simulation import SimulationContainer
from simaple.core.job_category import JobCategory
from simaple.core.jobtype import JobType
from simaple.simulate.policy.parser import parse_dsl_to_operations


@pytest.fixture(name="dsl_list")
def fixture_dsl_list() -> list[str]:
    with open(Path(__file__).parent / "archmage_tc_runtime.txt", encoding="utf-8") as f:
        dsl_list = [line.strip() for line in f.readlines()]

    return dsl_list


@pytest.fixture(name="dsl_test_setting")
def fixture_dsl_test_setting() -> BaselineEnvironmentProvider:
    return BaselineEnvironmentProvider(
        tier="Legendary",
        jobtype=JobType.archmagetc,
        job_category=JobCategory.magician,
        level=270,
        passive_skill_level=0,
        combat_orders_level=1,
        artifact_level=40,
    )


def test_dsl(
    dsl_list: list[str], dsl_test_setting: BaselineEnvironmentProvider
) -> None:
    environment = PersistentStorageMemoizer(
        os.path.join(os.path.dirname(__file__), ".simaple.memo.json"),
    ).compute_environment(
        dsl_test_setting,
    )
    container = SimulationContainer(environment)
    engine = container.operation_engine()

    for dsl in dsl_list:
        operations = parse_dsl_to_operations(dsl)
        for op in operations:
            engine.exec(op)

    dpm = container.damage_calculator().calculate_dpm(list(engine.simulation_entries()))
    print(f"{engine.get_current_viewer()('clock')} | {dpm:,} ")
    assert 12189847067621.467 == pytest.approx(dpm)
