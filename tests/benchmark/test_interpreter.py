import pytest

from simaple.core import BaseStatType, JobCategory
from simaple.gear.blueprint.gearset_blueprint import UserGearsetBlueprint
from simaple.gear.gear_repository import GearRepository
from simaple.gear.spec.interpreter import builtin_blueprint


@pytest.mark.parametrize(
    "benchmark_name",
    [
        "Epic",
        "EpicUnique",
        "Unique",
        "Legendary18",
        "LegendaryHalf",
        "Legendary",
    ],
)
def test_interpreter_get_gearset(benchmark_name):
    user_gearset_blueprint: UserGearsetBlueprint = builtin_blueprint(
        benchmark_name,
        job_category=JobCategory.warrior,
    )

    gear_repository = GearRepository()
    gearset = user_gearset_blueprint.build(gear_repository)


def test_gearset_ok():
    user_gearset_blueprint = builtin_blueprint(
        "Legendary",
        job_category=JobCategory.warrior,
    )

    gear_repository = GearRepository()
    gearset = user_gearset_blueprint.build(gear_repository)

    assert (
        gearset.get_total_stat().get_base_stat_coefficient(BaseStatType.STR) == 42760.2
    )
