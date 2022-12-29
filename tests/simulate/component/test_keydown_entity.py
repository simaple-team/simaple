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
def test_keydown_count(time, expected):
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
        (100, 450, 0, 100, (100, 100)),
        (150, 450, 0, 100, (100, 100)),
        (500, 450, 0, 100, (100, 100, 100, 100, 50)),
        (600, 2400, 600, 300, (300,)),
        (2400, 2400, 0, 300, (300, 300, 300, 300, 300, 300, 300, 300, 0)),
        (3000, 3000, 600, 300, (300, 300, 300, 300, 300, 300, 300, 300, 0)),
        (10000, 8160, 240, 1020, (1020, 1020, 1020, 1020, 1020, 1020, 1020, 780)),
    ],
)
def test_keydown_delay(
    elapse_time: float,
    maximum_keydown_time: float,
    prepare_delay: float,
    interval: float,
    expected: tuple[float],
):
    # given
    keydown = Keydown(interval=interval)
    keydown.start(
        maximum_keydown_time=maximum_keydown_time, prepare_delay=prepare_delay
    )

    # when
    delays = tuple(keydown.resolving(elapse_time))

    # then
    assert delays == expected


@pytest.mark.parametrize(
    "elapse_time, maximum_keydown_time, prepare_delay, interval, expected",
    [
        (1020, 8160, 240, 1020, (1020, 1020, 1020, 1020, 1020, 1020, 1020, 780)),
    ],
)
def test_keydown_multiple_elapse(
    elapse_time: float,
    maximum_keydown_time: float,
    prepare_delay: float,
    interval: float,
    expected: tuple[float],
):
    # given
    keydown = Keydown(interval=interval)
    keydown.start(
        maximum_keydown_time=maximum_keydown_time, prepare_delay=prepare_delay
    )

    # when
    delays = []
    for _ in range(30):
        delays += list(keydown.resolving(elapse_time))

    # then
    assert tuple(delays) == expected
