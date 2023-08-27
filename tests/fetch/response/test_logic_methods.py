import pytest

from simaple.fetch.inference.stat_logic import get_authentic_force_increment


@pytest.mark.parametrize(
    "level, authentic_force, expected",
    [
        (275, 200, 5200),
        (260, 60, 1500),
        (265, 60, 1800),
        (268, 60, 1800),
        (280, 380, 9100),
    ],
)
def test_authentic_force_increment(level, authentic_force, expected):
    assert get_authentic_force_increment(level, authentic_force) == expected
