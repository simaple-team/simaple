from simaple.core import Stat
from simaple.core.damage import INTBasedDamageLogic
from simaple.core.jobtype import JobType
from simaple.job.builtin.util import parse_resource_path
from simaple.job.job import Job
from simaple.job.passive_skill import PassiveSkillArgument, PassiveSkillset


def job_archmagefb(argument: PassiveSkillArgument):
    return Job(
        passive_skillset=PassiveSkillset.from_resource_file(
            parse_resource_path("passive_skill/archmagefb")
        ).all(argument),
        default_active_skillset=PassiveSkillset.from_resource_file(
            parse_resource_path("default_active_skill/archmagefb")
        ).all(argument),
        damage_logic=INTBasedDamageLogic(
            attack_range_constant=1.2,
            mastery=0.95 + 0.01 * (argument.combat_orders_level // 2),
        ),
        level=argument.character_level,
        level_stat=Stat(
            INT=(18 + 5 * argument.character_level),
            LUK=4,
            STR=4,
            DEX=4,
        ),
        type=JobType.archmagefb,
    )
