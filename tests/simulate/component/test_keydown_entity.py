import pytest

from simaple.simulate.component.keydown_skill import Keydown


@pytest.mark.parametrize(
    "time, expected",
    [
        (1500, 13),
        (300, 4),
        (750, 8),
    ],
)
def test_keydown_simple_count(time, expected):
    # given
    keydown = Keydown(interval=100)
    keydown.start(maximum_keydown_time=1200, prepare_delay=0)

    # when
    count = 0
    for _ in keydown.resolving(time):
        count += 1

    # then
    assert count == expected


@pytest.mark.parametrize(
    "elapse_time, maximum_keydown_time, prepare_delay, interval, expected",
    [
        (100, 450, 0, 100, 2),
        (150, 450, 0, 100, 2),
        (500, 450, 0, 100, 5),
        (600, 2400, 600, 300, 1),
        (899, 2400, 600, 300, 1),
        (900, 2400, 600, 300, 2),
        (2400, 2400, 0, 300, 9),
        (3000, 3000, 600, 300, 9),
        (10000, 8160, 240, 1020, 8),
    ],
)
def test_keydown_complex_count(
    elapse_time: float,
    maximum_keydown_time: float,
    prepare_delay: float,
    interval: float,
    expected: tuple[float],
):
    # given
    keydown = Keydown(interval=interval)
    keydown.start(maximum_keydown_time=maximum_keydown_time, prepare_delay=prepare_delay)

    # when
    resolved_count = len(list(keydown.resolving(elapse_time)))

    # then
    assert resolved_count == expected


@pytest.mark.parametrize(
    "schedule, maximum_keydown_time, prepare_delay, interval, expected",
    [
        ([1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 160], 8160, 240, 1020, 8),
        ([8160], 8160, 240, 1020, 8),
        ([500, 600, 700, 800, 900, 1000, 1500, 2000, 4000], 8160, 240, 1020, 8),
        ([240], 8160, 240, 1020, 1),
    ],
)
def test_keydown_multiple_elapse(
    schedule: list[float],
    maximum_keydown_time: float,
    prepare_delay: float,
    interval: float,
    expected: tuple[float],
):
    # given
    keydown = Keydown(interval=interval)
    keydown.start(maximum_keydown_time=maximum_keydown_time, prepare_delay=prepare_delay)

    # when
    resolved_count = 0
    for elapse_time in schedule:
        resolved_count += len(list(keydown.resolving(elapse_time)))

    # then
    assert resolved_count == expected
