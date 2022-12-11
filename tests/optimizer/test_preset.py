import pytest

from simaple.core import JobCategory, JobType, Stat
from simaple.core.damage import STRBasedDamageLogic
from simaple.data.baseline import get_baseline_gearset
from simaple.gear.potential import PotentialTier
from simaple.optimizer.preset import PresetOptimizer


@pytest.fixture(name="test_gearset")
def get_test_gearset():
    gearset = get_baseline_gearset(
        "Legendary",
        JobCategory.warrior,
        JobType.adele,
    )

    return gearset


def test_preset(test_gearset):
    optimizer = PresetOptimizer(
        union_block_count=7,
        default_stat=Stat(
            boss_damage_multiplier=150,
            ignored_defence=28,
            critical_rate=60,
        ),
        level=200,
        damage_logic=STRBasedDamageLogic(attack_range_constant=1.2, mastery=0.95),
        character_job_type=JobType.adele,
        alternate_character_job_types=[],
        link_count=12 + 1,
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
