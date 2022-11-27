from simaple.core import Stat
from simaple.job.builtin.interpreter import get_job_dependent_stat


def test_archmagefb():
    static_property_stat = get_job_dependent_stat(
        "archmagefb",
        combat_orders_level=1,
        passive_skill_level=0,
        character_level=260,
    )
    assert isinstance(static_property_stat, Stat)
