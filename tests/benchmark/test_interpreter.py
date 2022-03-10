from simaple.benchmark.interpreter import BenchmarkConfigurationInterpreter, BenchmarkInterpreterOption

from pydantic import BaseModel
from typing import Optional
from simaple.gear.gear import Gear
from simaple.gear.gear_type import GearType
from simaple.gear.blueprint import PracticalGearBlueprint
from simaple.gear.gear_repository import GearRepository

import yaml
import enum


def test_interpreter_run_ok():
    interpreter_option = BenchmarkInterpreterOption(
        stat_priority=['STR', 'DEX', 'INT', 'LUK'],
        attack_priority=['attack_power', 'magic_attack'],
        job_index=0
    )

    interpreter = BenchmarkConfigurationInterpreter()

    user_gearset_blueprint = interpreter.interpret_user_gearset_from_file('./simaple/benchmark/builtin/T30000.yaml', interpreter_option)
    gear_repository = GearRepository()
    final_stat = user_gearset_blueprint.build(gear_repository)
    print(final_stat)