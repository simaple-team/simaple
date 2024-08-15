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
        artifact_level=40,
    )


SETTINGS = [
    (
        (
            JobType.archmagefb,
            JobCategory.magician,
        ),
        12980199199663,
    ),
    (
        (
            JobType.archmagetc,
            JobCategory.magician,
        ),
        10536699514444,
    ),
    (
        (
            JobType.bishop,
            JobCategory.magician,
        ),
        7230098821342,
    ),
    (
        (
            JobType.mechanic,
            JobCategory.pirate,
        ),
        5712922745016,
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
        7149788810806,
    ),
    (
        (
            JobType.windbreaker,
            JobCategory.archer,
            {
                "weapon_attack_power": 789,
            },
        ),
        9001993985484,
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
