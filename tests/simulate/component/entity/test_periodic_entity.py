import pytest

from simaple.simulate.component.entity import Periodic


@pytest.mark.parametrize(
    "time, interval, expected_count",
    [
        (1500, 100, 12),
        (300, 100, 4),
        (750, 100, 8),
    ],
)
def test_periodic_iterator(time, interval, expected_count):
    # given
    periodic = Periodic(interval=interval)
    count = periodic.set_time_left_without_delay(1200)

    time_to_resolve = time
    previous_count = periodic.count
    # when
    while time_to_resolve > 0:
        periodic, time_to_resolve = periodic.resolve_step(periodic, time_to_resolve)
        if previous_count == periodic.count:
            continue

        count += 1
        previous_count = periodic.count

    # then
    assert count == expected_count


@pytest.mark.parametrize(
    "time, interval, expected_count",
    [
        (1500, 100, 12),
        (300, 100, 4),
        (750, 100, 8),
    ],
)
def test_elapse(time, interval, expected_count):
    # given
    periodic = Periodic(interval=interval)
    count = periodic.set_time_left_without_delay(1200)

    # when
    count += periodic.elapse(time)

    # then
    assert count == expected_count


@pytest.mark.parametrize(
    "time_left, initial_counter, time, expected",
    [
        (1, 20, 70, 0),
        (150, 50, 70, 1),
        (200, 300, 500, 0),
        (300, 300, 500, 0),
        (301, 300, 500, 1),
        (400, 300, 250, 0),
        (400, 300, 300, 1),
        (400, 400, 400, 0),
        (400, 300, 400, 1),
    ],
)
def test_periodic_initial_counter(time_left, initial_counter, time, expected):
    periodic = Periodic(interval=100)
    periodic.set_time_left(time_left, initial_counter)
    count = periodic.elapse(time)

    assert count == expected
