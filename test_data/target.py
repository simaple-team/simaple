import os

from simaple.container.simulation import SimulationSetting
from simaple.core.job_category import JobCategory
from simaple.core.jobtype import JobType


def container_test_setting(
    jobtype,
    job_category,
    options: dict = None,
):
    if options is None:
        options = {}

    return SimulationSetting(
        tier="Legendary",
        jobtype=jobtype,
        job_category=job_category,
        level=270,
        passive_skill_level=0,
        combat_orders_level=1,
        hexa_mastery_level=1,
        v_skill_level=30,
        v_improvements_level=60,
        cache_root_dir=os.path.join(os.path.dirname(__file__), "cache"),
        weapon_attack_power=options.get("weapon_attack_power", 0),
        weapon_pure_attack_power=options.get("weapon_pure_attack_power", 0),
    )


SETTINGS = [
    (
        (
            JobType.archmagefb,
            JobCategory.magician,
        ),
        13360232572802,
    ),
    (
        (
            JobType.archmagetc,
            JobCategory.magician,
        ),
        6534916107988,
    ),
    (
        (
            JobType.bishop,
            JobCategory.magician,
        ),
        5324413159316,
    ),
    (
        (
            JobType.mechanic,
            JobCategory.pirate,
        ),
        5644701182640,
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
        7373425362872,
    ),
    (
        (
            JobType.windbreaker,
            JobCategory.archer,
            {
                "weapon_attack_power": 789,
            },
        ),
        9290299778417,
    ),
    (
        (
            JobType.soulmaster,
            JobCategory.warrior,
            {
                "weapon_attack_power": 789,
            },
        ),
        11888632842960,
    ),
    (
        (
            JobType.dualblade,
            JobCategory.thief,
            {
                "weapon_attack_power": 700,
            },
        ),
        5354943334938,
    ),
]


def get_test_settings():
    return [(container_test_setting(*args), args[0], dpm) for args, dpm in SETTINGS]
