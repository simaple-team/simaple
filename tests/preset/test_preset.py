import pytest

from simaple.benchmark.interpreter import (
    BenchmarkConfigurationInterpreter,
    BenchmarkInterpreterOption,
)
from simaple.core import BaseStatType, JobCategory, JobType, Stat
from simaple.core.damage import STRBasedDamageLogic
from simaple.gear.gear_repository import GearRepository
from simaple.gear.potential import Potential, PotentialTier
from simaple.preset.base import PresetOptimizer


@pytest.fixture(name="test_gearset")
def get_test_gearset():
    interpreter_option = BenchmarkInterpreterOption(
        stat_priority=["STR", "DEX", "INT", "LUK"],
        attack_priority=["attack_power", "magic_attack"],
        job_category=JobCategory.warrior,
    )

    interpreter = BenchmarkConfigurationInterpreter()

    user_gearset_blueprint = interpreter.interpret_user_gearset_from_file(
        "./simaple/benchmark/builtin/T30000.yaml", interpreter_option
    )
    gear_repository = GearRepository()
    gearset = user_gearset_blueprint.build(gear_repository)
    return gearset


def test_preset(test_gearset):
    optimizer = PresetOptimizer(
        union_block_count=37,
        default_stat=Stat(
            boss_damage_multiplier=150,
            ignored_defence=28,
        ),
        level=275,
        level_stat=Stat(STR=274 * 5 + 23, DEX=4),
        damage_logic=STRBasedDamageLogic(attack_range_constant=1.2, mastery=0.95),
        character_job_type=JobType.adele,
        alternate_character_job_types=[],
        link_count=12 + 1,
        weapon_potential_tiers=[
            (PotentialTier.legendary, PotentialTier.unique, PotentialTier.unique),
            (PotentialTier.legendary, PotentialTier.unique, PotentialTier.unique),
            (PotentialTier.legendary, PotentialTier.unique, PotentialTier.unique),
        ],
    )

    preset = optimizer.create_optimal_preset_from_gearset(test_gearset)

    print("hyperstat")
    print(preset.hyperstat.get_stat().show())

    print("links")
    print(preset.links.get_stat().show())
    print("union_blocks")
    print(preset.union_blocks.get_stat().show())
    print("union_occupation")

    print(preset.union_occupation.get_stat().show())
    print("get_total_stat")
    print(preset.get_total_stat().show())

    expected = Stat(
        STR=5029.0,
        LUK=1141.0,
        INT=1468.0,
        DEX=2579.0,
        STR_multiplier=613.0,
        LUK_multiplier=89.0,
        INT_multiplier=89.0,
        DEX_multiplier=89.0,
        STR_static=18350.0,
        LUK_static=410.0,
        INT_static=530.0,
        DEX_static=640.0,
        attack_power=2453.5,
        magic_attack=1213.0,
        attack_power_multiplier=81.0,
        magic_attack_multiplier=0.0,
        critical_rate=98.0,
        critical_damage=76.0,
        boss_damage_multiplier=222.0,
        damage_multiplier=113.5,
        final_damage_multiplier=0.0,
        ignored_defence=94.28068497088,
        MHP=13455.0,
        MMP=255.0,
    )

    assert expected == preset.get_total_stat()
