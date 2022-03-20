import pytest

from simaple.core.base import ActionStat

TEST_CASES = [
    ("cooltime_reduce", 3, 4, 7),
    ("summon_duration", 3, 4, 7),
    ("buff_duration", 3, 4, 7),
    ("cooltime_reduce_rate", 3, 4, 7),
]


@pytest.mark.parametrize("stat_name, a, b, c", TEST_CASES)
def test_ability(stat_name, a, b, c):
    stat_a = ActionStat(**{stat_name: a})
    stat_b = ActionStat(**{stat_name: b})

    stat_c = ActionStat(**{stat_name: c})

    result = stat_a + stat_b

    assert getattr(result, stat_name) == getattr(stat_c, stat_name)
