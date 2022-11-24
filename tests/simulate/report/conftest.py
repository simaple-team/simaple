import pytest

from simaple.core import BaseStatType, JobCategory, JobType, Stat
from simaple.core.damage import STRBasedDamageLogic, INTBasedDamageLogic
from simaple.gear.gear_repository import GearRepository
from simaple.gear.potential import Potential, PotentialTier
from simaple.preset.base import PresetOptimizer
from simaple.benchmark.spec.interpreter import builtin_blueprint

from simaple.simulate.report.dpm import DPMCalculator


@pytest.fixture(name="user_gearset")
def get_test_gearset():
    user_gearset_blueprint = builtin_blueprint(
        "Legendary",
        job_category=JobCategory.warrior,
    )

    gear_repository = GearRepository()
    gearset = user_gearset_blueprint.build(gear_repository)
    return gearset


@pytest.fixture(name="user_preset")
def get_test_preset(user_gearset):
    optimizer = PresetOptimizer(
        union_block_count=7,
        default_stat=Stat(
            boss_damage_multiplier=150,
            ignored_defence=28,
        ),
        level=200,
        level_stat=Stat(STR=200 * 5 + 18, DEX=4),
        damage_logic=STRBasedDamageLogic(attack_range_constant=1.2, mastery=0.95),
        character_job_type=JobType.adele,
        alternate_character_job_types=[],
        link_count=12 + 1,
        weapon_potential_tier=(
            PotentialTier.legendary,
            PotentialTier.unique,
            PotentialTier.unique,
        ),
    )

    preset = optimizer.create_optimal_preset_from_gearset(user_gearset)
    return preset


@pytest.fixture
def archmagefb_dpm_calculator(user_preset):
    return DPMCalculator(
        character_spec=user_preset.get_total_stat(),
        armor=300,
        damage_logic=INTBasedDamageLogic(
            attack_range_constant=1.2,
            mastery=0.95
        ),
        v_skill_enhancements={
            "플레임 스윕": 60
        }
    )
