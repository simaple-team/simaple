import pytest

from simaple.spec.interpreter import (
    BenchmarkConfigurationInterpreter,
    BenchmarkInterpreterOption,
)
from simaple.core import BaseStatType, JobCategory
from simaple.gear.gear_repository import GearRepository


@pytest.mark.parametrize(
    "benchmark_file",
    [
        "./simaple/benchmark/builtin/Epic.yaml",
        "./simaple/benchmark/builtin/EpicUnique.yaml",
        "./simaple/benchmark/builtin/Unique.yaml",
        "./simaple/benchmark/builtin/Legendary18.yaml",
        "./simaple/benchmark/builtin/LegendaryHalf.yaml",
        "./simaple/benchmark/builtin/Legendary.yaml",
    ],
)
def test_interpreter_get_gearset(benchmark_file):
    interpreter_option = BenchmarkInterpreterOption(
        stat_priority=["STR", "DEX", "INT", "LUK"],
        attack_priority=["attack_power", "magic_attack"],
        job_category=JobCategory.warrior,
    )

    interpreter = BenchmarkConfigurationInterpreter()

    user_gearset_blueprint = interpreter.interpret_user_gearset_from_file(
        benchmark_file, interpreter_option
    )
    gear_repository = GearRepository()
    gearset = user_gearset_blueprint.build(gear_repository)


def test_gearset_ok():
    interpreter_option = BenchmarkInterpreterOption(
        stat_priority=["STR", "DEX", "INT", "LUK"],
        attack_priority=["attack_power", "magic_attack"],
        job_category=JobCategory.warrior,
    )

    interpreter = BenchmarkConfigurationInterpreter()

    user_gearset_blueprint = interpreter.interpret_user_gearset_from_file(
        "./simaple/benchmark/builtin/Legendary.yaml", interpreter_option
    )
    gear_repository = GearRepository()
    gearset = user_gearset_blueprint.build(gear_repository)

    print(gearset.get_total_stat().get_base_stat_coefficient(BaseStatType.STR))
