import os

from simaple.container.simulation import SimulationSetting
from simaple.core import ActionStat, ElementalResistance
from simaple.core.job_category import JobCategory
from simaple.core.jobtype import JobType


def container_test_setting(
    jobtype,
    job_category,
    action_stat,
    elemental_resistance,
    weapon_attack_power=0,
    weapon_pure_attack_power=0,
):
    return SimulationSetting(
        tier="Legendary",
        jobtype=jobtype,
        job_category=job_category,
        level=270,
        action_stat=action_stat,
        passive_skill_level=0,
        combat_orders_level=1,
        v_skill_level=30,
        v_improvements_level=60,
        elemental_resistance=elemental_resistance,
        cache_root_dir=os.path.join(os.path.dirname(__file__), "cache"),
        weapon_attack_power=weapon_attack_power,
        weapon_pure_attack_power=weapon_pure_attack_power,
    )


SETTINGS = [
    (
        (
            JobType.archmagefb,
            JobCategory.magician,
            ActionStat(buff_duration=185),
            ElementalResistance(value=10),
        ),
        7_987_317_029_876,
    ),
    (
        (
            JobType.archmagetc,
            JobCategory.magician,
            ActionStat(buff_duration=185),
            ElementalResistance(value=10),
        ),
        6_531_696_595_832,
    ),
    (
        (
            JobType.bishop,
            JobCategory.magician,
            ActionStat(buff_duration=185),
            ElementalResistance(value=10),
        ),
        5_425_335_904_477,
    ),
    (
        (
            JobType.mechanic,
            JobCategory.pirate,
            ActionStat(),
            ElementalResistance(value=0),
        ),
        5_362_067_609_119,
    ),
    (
        (
            JobType.adele,
            JobCategory.warrior,
            ActionStat(),
            ElementalResistance(value=0),
            700,
            295,
        ),
        6_903_469_727_134,
    ),
    (
        (
            JobType.windbreaker,
            JobCategory.archer,
            ActionStat(),
            ElementalResistance(value=0),
            789,
        ),
        8_410_332_871_049,
    ),
    (
        (
            JobType.soulmaster,
            JobCategory.warrior,
            ActionStat(),
            ElementalResistance(value=0),
            789,
        ),
        9_818_479_924_871,
    ),
    (
        (
            JobType.dualblade,
            JobCategory.thief,
            ActionStat(),
            ElementalResistance(value=0),
            700,
        ),
        4_529_731_978_243,
    ),
]


def get_test_settings():
    return [(container_test_setting(*args), args[0], dpm) for args, dpm in SETTINGS]
