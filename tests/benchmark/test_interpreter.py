from simaple.benchmark.interpreter import (
    BenchmarkConfigurationInterpreter,
    BenchmarkInterpreterOption,
)
from simaple.core import BaseStatType
from simaple.gear.gear_repository import GearRepository


def test_interpreter_get_gearset():
    interpreter_option = BenchmarkInterpreterOption(
        stat_priority=["STR", "DEX", "INT", "LUK"],
        attack_priority=["attack_power", "magic_attack"],
        job_index=0,
    )

    interpreter = BenchmarkConfigurationInterpreter()

    user_gearset_blueprint = interpreter.interpret_user_gearset_from_file(
        "./simaple/benchmark/builtin/T30000.yaml", interpreter_option
    )
    gear_repository = GearRepository()
    gearset = user_gearset_blueprint.build(gear_repository)


def test_gearset_ok():
    interpreter_option = BenchmarkInterpreterOption(
        stat_priority=["STR", "DEX", "INT", "LUK"],
        attack_priority=["attack_power", "magic_attack"],
        job_index=0,
    )

    interpreter = BenchmarkConfigurationInterpreter()

    user_gearset_blueprint = interpreter.interpret_user_gearset_from_file(
        "./simaple/benchmark/builtin/T30000.yaml", interpreter_option
    )
    gear_repository = GearRepository()
    gearset = user_gearset_blueprint.build(gear_repository)

    print(gearset.get_total_stat().get_base_stat_coefficient(BaseStatType.STR))
