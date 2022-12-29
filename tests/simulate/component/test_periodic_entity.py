import pytest

from simaple.simulate.component.skill import Periodic


@pytest.mark.parametrize(
    "time, expected",
    [
        (1500, 12),
        (300, 3),
        (750, 7),
    ],
)
def test_periodic_iterator(time, expected):
    # given
    periodic = Periodic(interval=100)
    periodic.set_time_left(1200)

    # when
    count = 0
    for _ in periodic.resolving(time):
        count += 1

    # then
    assert count == expected
