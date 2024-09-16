import os

from simaple.container.simulation import SimulationSetting
from simaple.container.character_provider import BaselineSimulationConfig
from simaple.core.job_category import JobCategory
from simaple.core.jobtype import JobType


def container_test_setting(
    jobtype,
    job_category,
    options: dict = None,
):
    if options is None:
        options = {}

    return BaselineSimulationConfig(
        tier="Legendary",
        jobtype=jobtype,
        job_category=job_category,
        level=270,
        passive_skill_level=0,
        combat_orders_level=1,
        cache_root_dir=os.path.join(os.path.dirname(__file__), "cache"),
        weapon_pure_attack_power=options.get("weapon_pure_attack_power", 0),
        artifact_level=40,
    ), SimulationSetting(
        hexa_mastery_level=1,
        v_skill_level=30,
        v_improvements_level=60,
        hexa_improvements_level=10,
        weapon_attack_power=options.get("weapon_attack_power", 0),
    )


SETTINGS = [
    (
        (
            JobType.archmagefb,
            JobCategory.magician,
        ),
        13597860884754,
    ),
    (
        (
            JobType.archmagetc,
            JobCategory.magician,
        ),
        11450940437523,
    ),
    (
        (
            JobType.bishop,
            JobCategory.magician,
        ),
        7847639017173,
    ),
    (
        (
            JobType.mechanic,
            JobCategory.pirate,
        ),
        6898897517450,
    ),
    (
        (
            JobType.adele,
            JobCategory.warrior,
            {
                "weapon_attack_power": 700,
                "weapon_pure_attack_power": 295,
            },
        ),
        7421348754564,
    ),
    (
        (
            JobType.windbreaker,
            JobCategory.archer,
            {
                "weapon_attack_power": 789,
            },
        ),
        9835974035601,
    ),
    (
        (
            JobType.soulmaster,
            JobCategory.warrior,
            {
                "weapon_attack_power": 789,
            },
        ),
        11522692385817,
    ),
    (
        (
            JobType.dualblade,
            JobCategory.thief,
            {
                "weapon_attack_power": 700,
            },
        ),
        5137550169303,
    ),
]


def get_test_settings():
    return [(container_test_setting(*args), args[0], dpm) for args, dpm in SETTINGS]
