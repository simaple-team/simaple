import pytest

from simaple.benchmark.interpreter import (
    BenchmarkConfigurationInterpreter,
    BenchmarkInterpreterOption,
)
from simaple.core import JobCategory
from simaple.gear.gear_repository import GearRepository
from simaple.gear.potential import PotentialTier
from simaple.job.builtin.archmagefb import job_archmagefb
from simaple.job.passive_skill import PassiveSkillArgument
from simaple.preset.base import PresetOptimizer


@pytest.fixture(name="test_gearset")
def get_test_gearset():
    interpreter_option = BenchmarkInterpreterOption(
        stat_priority=["INT", "LUK", "STR", "DEX"],
        attack_priority=["magic_attack", "attack_power"],
        job_category=JobCategory.mage,
    )

    interpreter = BenchmarkConfigurationInterpreter()

    user_gearset_blueprint = interpreter.interpret_user_gearset_from_file(
        "./simaple/benchmark/builtin/Legendary.yaml", interpreter_option
    )
    gear_repository = GearRepository()
    gearset = user_gearset_blueprint.build(gear_repository)
    return gearset


def test_preset(test_gearset):
    argument = PassiveSkillArgument(
        combat_orders_level=1,
        passive_skill_level=0,
        character_level=260,
    )

    job = job_archmagefb(argument)

    optimizer = PresetOptimizer.based_on_job(
        job,
        union_block_count=37,
        alternate_character_job_types=[],
        link_count=12 + 1,
        weapon_potential_tier=(
            PotentialTier.legendary,
            PotentialTier.unique,
            PotentialTier.unique,
        ),
    )

    preset = optimizer.create_optimal_preset_from_gearset(test_gearset)

    print("hyperstat")
    print(preset.hyperstat.get_stat().show())

    print("links")
    print(preset.links.get_stat().show())
    print("union_blocks")
    print(preset.union_squad.get_stat().show())
    print("union_occupation")

    print(preset.union_occupation.get_stat().show())
    print("get_total_stat")
    print(preset.get_total_stat().show())

    print("overall")
    print((preset.get_total_stat() + job.get_default_stat()).show())
