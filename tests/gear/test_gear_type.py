import pytest

from simaple.gear.gear_type import GearType


@pytest.mark.parametrize(
    "gear_type, expected",
    [
        (GearType.hand_cannon, True),
        (GearType.knuckle, True),
        (GearType.emblem, True),
        (GearType.chess, True),
        (GearType.evan_paper, True),
        (GearType.glove, False),
        (GearType.cape, False),
        (GearType.pants, False),
    ],
)
def test_is_weaponry(gear_type, expected):
    assert GearType.is_weaponry(gear_type) == expected
