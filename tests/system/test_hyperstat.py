import pytest

from simaple.system.hyperstat import Hyperstat


@pytest.mark.parametrize(
    "character_level, cost",
    [
        (100, 0),
        (140, 3),
        (149, 30),
        (200, 339),
        (244, 815),
        (269, 1170),
        (270, 1186),
        (275, 1266),
    ],
)
def test_hyperstat_cost_from_level(character_level, cost):
    assert Hyperstat.get_maximum_cost_from_level(character_level) == cost
