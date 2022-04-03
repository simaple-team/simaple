import pytest

from simaple.gear.improvements.bonus import BonusType


@pytest.mark.parametrize(
    "given, expected",
    [
        ("no-key", "no-key"),
        ("STR_DEX", "STR_DEX"),
        ("DEX_STR", "STR_DEX"),
        ("INT_LUK", "INT_LUK"),
        ("LUK_INT", "INT_LUK"),
        ("INT_LUK_DEX_STR", "INT_LUK_DEX_STR"),
    ],
)
def test_bonus_key_refinement(given, expected):
    assert BonusType.refine_double_key(given) == expected
