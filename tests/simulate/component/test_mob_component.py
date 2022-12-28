import pytest

from simaple.simulate.component.mob import DOT, MobComponent
from tests.simulate.component.util import count_dot_skill


@pytest.fixture(name="mob_component")
def fixture_mob_component(bare_store):
    return MobComponent(name="mob").compile(bare_store)


@pytest.mark.parametrize(
    "elapse_time, count",
    [
        (0, 0),
        (500, 0),
        (1000, 1),
        (1001, 1),
        (3000, 3),
        (3300, 3),
        (10000, 5),
    ],
)
def test_dot(elapse_time, count):
    dot = DOT()
    dot.new("dot0", 300, 5000)
    emits = dot.elapse(elapse_time)

    if count == 0:
        assert emits == {}
    else:
        assert emits == {("dot0", 300): count}


@pytest.mark.parametrize(
    "elapse_time, count_0, count_1",
    [
        (1000, 1, 1),
        (1001, 1, 1),
        (5000, 5, 5),
        (5001, 5, 5),
        (7000, 5, 7),
    ],
)
def test_multiple_dot(elapse_time, count_0, count_1):
    dot = DOT()
    dot.new("dot0", 300, 5000)
    dot.new("dot1", 400, 8000)
    emits = dot.elapse(elapse_time)

    assert emits == {
        ("dot0", 300): count_0,
        ("dot1", 400): count_1,
    }


@pytest.mark.parametrize(
    "time, expected_event_count", [(500, 0), (1000, 1), (1001, 1), (3000, 1)]
)
def test_add_dot(mob_component, time, expected_event_count):
    mob_component.add_dot({"name": "A", "damage": 100, "lasting_time": 10_000})
    events = mob_component.elapse(time)

    assert count_dot_skill(events) == expected_event_count


def test_dot_count(mob_component):
    mob_component.add_dot({"name": "A", "damage": 100, "lasting_time": 10_000})
    events = []
    for _ in range(45):
        events += mob_component.elapse(100)

    assert count_dot_skill(events) == 4


def test_complex_dot_scenario(mob_component):
    mob_component.add_dot({"name": "A", "damage": 100, "lasting_time": 10_000})
    mob_component.add_dot({"name": "B", "damage": 100, "lasting_time": 7_000})
    events = mob_component.elapse(5000)
    assert count_dot_skill(events) == 2

    events = mob_component.elapse(3000)
    assert count_dot_skill(events) == 2

    events = mob_component.elapse(3000)
    assert count_dot_skill(events) == 1


def test_dot_override(mob_component):
    mob_component.add_dot({"name": "A", "damage": 100, "lasting_time": 10_000})

    events = mob_component.elapse(5000)
    assert count_dot_skill(events) == 1
    assert events[0].payload["hit"] == 5

    mob_component.add_dot({"name": "A", "damage": 100, "lasting_time": 10_000})

    events = mob_component.elapse(7000)
    assert count_dot_skill(events) == 1
    assert events[0].payload["hit"] == 7

    events = mob_component.elapse(3000)
    assert count_dot_skill(events) == 1
    assert events[0].payload["hit"] == 3

    events = mob_component.elapse(3000)
    assert count_dot_skill(events) == 0
