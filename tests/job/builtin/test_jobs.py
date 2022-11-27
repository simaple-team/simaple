from simaple.job.builtin.interpreter import get_static_propery


def test_archmagefb():
    static_property = get_static_propery(
        "archmagefb",
        combat_orders_level=1,
        passive_skill_level=0,
        character_level=260,
    )
    stat = static_property.get_default_stat()
