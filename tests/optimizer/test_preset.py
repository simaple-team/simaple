import pytest

from simaple.core import JobCategory, JobType, Stat
from simaple.core.damage import STRBasedDamageLogic
from simaple.data.baseline import get_baseline_gearset
from simaple.optimizer.preset import PresetOptimizer


@pytest.fixture(name="test_gearset")
def get_test_gearset():
    gearset = get_baseline_gearset(
        "Legendary",
        JobCategory.warrior,
        JobType.adele,
    )

    return gearset


@pytest.mark.parametrize(
    "level, expected_stat",
    [
        (
            12,
            {  # 10 10 10 3 3 3
                "boss_damage_multiplier": 15.0,
                "damage_multiplier": 15.0,
                "ignored_defence": 20.0,
                "critical_damage": 1.2,
                "critical_rate": 6.0,
                "attack_power": 9.0,
                "magic_attack": 9.0,
            },
        ),
        (
            20,
            {  # 10 10 10 8 8 8
                "boss_damage_multiplier": 15.0,
                "damage_multiplier": 15.0,
                "ignored_defence": 20.0,
                "critical_damage": 3.2,
                "critical_rate": 16.0,
                "attack_power": 24.0,
                "magic_attack": 24.0,
            },
        ),
    ],
)
def test_preset_artifact(level, expected_stat):
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
        artifact_level=level,
    )

    optimal_artifact = optimizer.calculate_optimal_artifact(
        Stat(
            boss_damage_multiplier=150,
            ignored_defence=67,
            critical_rate=60,
            STR=10000,
            attack_power=1000,
        )
    )

    assert optimal_artifact.get_extended_stat().stat.short_dict() == expected_stat


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
        artifact_level=35,
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
    print(preset.get_stat().show())
