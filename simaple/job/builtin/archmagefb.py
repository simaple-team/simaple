from simaple.core.damage import INTBasedDamageLogic
from simaple.job.builtin.util import parse_resource_path
from simaple.job.job import Job
from simaple.job.passive_skill import PassiveSkillset


def job_archmagefb():
    return Job(
        passive_skillset=PassiveSkillset.from_resource_file("passive_skill/archmagefb"),
        default_active_skillset=PassiveSkillset.from_resource_file(
            "default_active_skill/archmagefb"
        ),
        damage_logic=INTBasedDamageLogic(),
    )
