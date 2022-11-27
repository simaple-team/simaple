from simaple.core import Stat
from simaple.data.passive import get_passive_and_default_active_stat


def test_archmagefb():
    static_property_stat = get_passive_and_default_active_stat(
        "archmagefb",
        combat_orders_level=1,
        passive_skill_level=0,
        character_level=260,
    )
    assert isinstance(static_property_stat, Stat)
