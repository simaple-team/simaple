from simaple.container.environment_provider import BaselineEnvironmentProvider
from simaple.core.jobtype import JobType


def container_test_setting(
    jobtype,
    options: dict = None,
):
    if options is None:
        options = {}

    return BaselineEnvironmentProvider(
        tier="Legendary",
        jobtype=jobtype,
        level=270,
        passive_skill_level=0,
        combat_orders_level=1,
        weapon_pure_attack_power=options.get("weapon_pure_attack_power", 0),
        artifact_level=40,
        hexa_mastery_level=1,
        v_skill_level=30,
        v_improvements_level=60,
        hexa_improvements_level=10,
        weapon_attack_power=options.get("weapon_attack_power", 0),
    )


SETTINGS = [
    (
        (JobType.archmagefb,),
        15919731027452,
    ),
    (
        (JobType.archmagetc,),
        13395121192957,
    ),
    (
        (JobType.bishop,),
        9251885099074,
    ),
    (
        (JobType.mechanic,),
        9015172035127,
    ),
    (
        (
            JobType.adele,
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
            {
                "weapon_attack_power": 789,
            },
        ),
        11411869302005,
    ),
    (
        (
            JobType.soulmaster,
            {
                "weapon_attack_power": 789,
            },
        ),
        13343175412181,
    ),
    (
        (
            JobType.dualblade,
            {
                "weapon_attack_power": 700,
            },
        ),
        5887717338595,
    ),
]


def get_test_settings():
    return [(container_test_setting(*args), args[0], dpm) for args, dpm in SETTINGS]
