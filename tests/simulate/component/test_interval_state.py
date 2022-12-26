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
def test_interval_state_iterator(time, expected):
    interval_state = Periodic(interval=100)

    interval_state.set_time_left(1200)

    count = 0
    for _ in interval_state.resolving(time):
        count += 1

    assert count == expected
