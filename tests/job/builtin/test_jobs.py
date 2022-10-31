from simaple.job.builtin.interpreter import get_static_propery
from simaple.job.description import GeneralJobArgument


def test_archmagefb():
    argument = GeneralJobArgument(
        combat_orders_level=1,
        passive_skill_level=0,
        character_level=260,
    )
    static_property = get_static_propery("archmagefb", argument)
    stat = static_property.get_default_stat()
