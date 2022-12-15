import pytest

from simaple.simulate.report.dpm import LevelAdvantage


@pytest.mark.parametrize(
    "mob_lv, char_lv, expected",
    [
        (30, 200, 1.2),
        (30, 35, 1.2),
        (30, 29, 1.0584),
        (100, 75, 0.38),
        (100, 50, 0),
    ],
)
def test_level_advantage(mob_lv: int, char_lv: int, expected: float):
    advantage = LevelAdvantage()
    assert advantage.get_advantage(mob_lv, char_lv) == expected
