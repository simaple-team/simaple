from simaple.core import ExtendedStat, JobType
from simaple.data.jobs.builtin import get_passive


def test_archmagefb():
    static_property_stat = get_passive(
        JobType.archmagefb,
        combat_orders_level=1,
        passive_skill_level=0,
        character_level=260,
    )
    assert isinstance(static_property_stat, ExtendedStat)
