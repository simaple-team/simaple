from simaple.job.builtin.archmagefb import archmagefb_static_property
from simaple.job.passive_skill import PassiveSkillArgument


def test_archmagefb():
    argument = PassiveSkillArgument(
        combat_orders_level=1,
        passive_skill_level=0,
        character_level=260,
    )
    static_property = archmagefb_static_property(argument)
    static_property.get_default_stat()
