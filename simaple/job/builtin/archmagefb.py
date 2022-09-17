from simaple.job.builtin.util import parse_resource_path
from simaple.job.passive_skill import PassiveSkillArgument, PassiveSkillset
from simaple.job.static_property import StaticProperty


def archmagefb_static_property(argument: PassiveSkillArgument):
    return StaticProperty(
        passive_skillset=PassiveSkillset.from_resource_file(
            parse_resource_path("passive_skill/archmagefb")
        ).all(argument),
        default_active_skillset=PassiveSkillset.from_resource_file(
            parse_resource_path("default_active_skill/archmagefb")
        ).all(argument),
    )
