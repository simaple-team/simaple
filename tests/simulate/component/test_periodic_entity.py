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


@pytest.mark.parametrize(
    "time_left, initial_counter, time, expected",
    [
        (150, 50, 70, 1),
        (200, 300, 500, 0),
        (300, 300, 500, 1),
        (400, 300, 250, 0),
        (400, 300, 300, 1),
        (400, 300, 400, 2),
    ],
)
def test_periodic_initial_counter(time_left, initial_counter, time, expected):
    periodic = Periodic(interval=100)
    periodic.set_time_left(time_left, initial_counter)

    count = 0
    for _ in periodic.resolving(time):
        count += 1

    assert count == expected
