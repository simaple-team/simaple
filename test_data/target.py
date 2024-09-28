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
        16039979770012,
    ),
    (
        (JobType.archmagetc,),
        13496300445113,
    ),
    (
        (JobType.bishop,),
        9187430863944,
    ),
    (
        (JobType.mechanic,),
        7563274726317,
    ),
    (
        (
            JobType.adele,
            {
                "weapon_attack_power": 700,
                "weapon_pure_attack_power": 295,
            },
        ),
        9068638620941,
    ),
    (
        (
            JobType.windbreaker,
            {
                "weapon_attack_power": 789,
            },
        ),
        11031190295810,
    ),
    (
        (
            JobType.soulmaster,
            {
                "weapon_attack_power": 789,
            },
        ),
        12689549643945,
    ),
    (
        (
            JobType.dualblade,
            {
                "weapon_attack_power": 700,
            },
        ),
        5560719214823,
    ),
]


def get_test_settings():
    return [(container_test_setting(*args), args[0], dpm) for args, dpm in SETTINGS]
