import pytest

from simaple.core import ActionStat

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


@pytest.mark.parametrize(
    "original_cooldown, cooltime_reduce_rate, cooltime_reduce, expected_cooldown",
    [
        (100000, 5, 5000, 90000),
        (12000, 5, 4000, 8700),
        (10000, 5, 4000, 7600),
        (5300, 5, 4000, 5000),
        (5000, 5, 4000, 4750),
        (1000, 5, 0, 1000),
    ],
)
def test_cooltime_reduce(
    original_cooldown, cooltime_reduce_rate, cooltime_reduce, expected_cooldown
):
    stat = ActionStat(
        cooltime_reduce_rate=cooltime_reduce_rate,
        cooltime_reduce=cooltime_reduce,
    )

    assert stat.calculate_cooldown(original_cooldown) == expected_cooldown
