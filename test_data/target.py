import os

from simaple.container.environment_provider import BaselineEnvironmentProvider, MemoizationIndependentEnvironment
from simaple.core.job_category import JobCategory
from simaple.core.jobtype import JobType


def container_test_setting(
    jobtype,
    job_category,
    options: dict = None,
):
    if options is None:
        options = {}

    return BaselineEnvironmentProvider(
        tier="Legendary",
        jobtype=jobtype,
        job_category=job_category,
        level=270,
        passive_skill_level=0,
        combat_orders_level=1,
        weapon_pure_attack_power=options.get("weapon_pure_attack_power", 0),
        artifact_level=40,
        independent_environment=MemoizationIndependentEnvironment(
            hexa_mastery_level=1,
            v_skill_level=30,
            v_improvements_level=60,
            hexa_improvements_level=10,
            weapon_attack_power=options.get("weapon_attack_power", 0),
        )
    ) 


SETTINGS = [
    (
        (
            JobType.archmagefb,
            JobCategory.magician,
        ),
        15919731027452,
    ),
    (
        (
            JobType.archmagetc,
            JobCategory.magician,
        ),
        13395121192957,
    ),
    (
        (
            JobType.bishop,
            JobCategory.magician,
        ),
        9251885099074,
    ),
    (
        (
            JobType.mechanic,
            JobCategory.pirate,
        ),
        8064280322731,
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
        8782689556242,
    ),
    (
        (
            JobType.windbreaker,
            JobCategory.archer,
            {
                "weapon_attack_power": 789,
            },
        ),
        11411869302005,
    ),
    (
        (
            JobType.soulmaster,
            JobCategory.warrior,
            {
                "weapon_attack_power": 789,
            },
        ),
        13343175412181,
    ),
    (
        (
            JobType.dualblade,
            JobCategory.thief,
            {
                "weapon_attack_power": 700,
            },
        ),
        5887717338595,
    ),
]


def get_test_settings():
    return [(container_test_setting(*args), args[0], dpm) for args, dpm in SETTINGS]
