from simaple.core.damage import INTBasedDamageLogic
from simaple.job.builtin.util import parse_resource_path
from simaple.job.job import Job
from simaple.job.passive_skill import PassiveSkillset
from simaple.job.description import GeneralJobArgument


def _archmage_damage_logic(argument: GeneralJobArgument) -> INTBasedDamageLogic:
    return INTBasedDamageLogic(
        attack_range_constant=1.2,
        mastery=0.95 + 0.01 * (combat_orders_level // 2)
    )

def job_archmagefb():
    return Job(
        passive_skillset=PassiveSkillset.from_resource_file(
            parse_resource_path("passive_skill/archmagefb")
        ),
        default_active_skillset=PassiveSkillset.from_resource_file(
            parse_resource_path("default_active_skill/archmagefb")
        ),
        damage_logic_template=_archmage_damage_logic,
    )
