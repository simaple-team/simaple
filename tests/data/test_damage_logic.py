from simaple.core.base import Stat
from simaple.core.jobtype import JobType
from simaple.data import get_damage_logic


def test_damage_logic():
    logic = get_damage_logic(JobType.archmagefb, 0)
    assert logic.mastery == 0.95
    assert logic.attack_range_constant == 1.2

    assert logic.get_major_stat(Stat(INT=3, LUK=5)) == 3


def test_damage_logic_with_combat_orders():
    logic = get_damage_logic(JobType.archmagefb, 1)
    assert logic.mastery == 0.96
    assert logic.attack_range_constant == 1.2

    assert logic.get_major_stat(Stat(INT=3, LUK=5)) == 3
