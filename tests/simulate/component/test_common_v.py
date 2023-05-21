import pytest

from simaple.simulate.component.specific.common_v import (
    ProgrammedPeriodicComponent,
    ProgrammedPeriodicState,
)
from simaple.simulate.global_property import Dynamics
from simaple.simulate.reserved_names import Tag


@pytest.fixture(name="component")
def fixture_component():
    return ProgrammedPeriodicComponent(
        id="test",
        name="spider-in-mirror",
        damage=100,
        hit=1,
        delay=30,
        periodic_intervals=[100, 200, 300],
        periodic_damage=50,
        periodic_hit=3,
        lasting_duration=3_000,
        cooldown_duration=30_000,
    )


@pytest.fixture(name="state")
def fixture_state(
    component: ProgrammedPeriodicComponent,
    dynamics: Dynamics,
):
    return ProgrammedPeriodicState(**component.get_default_state(), dynamics=dynamics)


def test_component_reject(
    component: ProgrammedPeriodicComponent,
    state: ProgrammedPeriodicState,
):
    # given
    state, events = component.use(None, state)
    state, events = component.use(None, state)

    # then
    assert events[0].tag == Tag.REJECT


def test_component_emit_initial_damage(
    component: ProgrammedPeriodicComponent,
    state: ProgrammedPeriodicState,
):
    # given
    _, events = component.use(None, state)

    # then
    assert events[0].payload == {"damage": 100, "hit": 1.0, "modifier": None}
    assert events[1].payload == {"time": 30.0}


@pytest.mark.parametrize(
    "time, count",
    [
        (100, 2),
        (200, 2),
        (300, 3),
        (400, 3),
        (500, 3),
        (600, 4),
        (700, 5),
        (1300, 8),
        (2400, 13),
    ],
)
def test_component_emit_after(
    component: ProgrammedPeriodicComponent,
    state: ProgrammedPeriodicState,
    time: float,
    count: int,
):
    # given
    state, _ = component.use(None, state)
    state, events = component.elapse(time, state)

    # then
    dealing_count = sum([e.tag == Tag.DAMAGE for e in events])
    assert dealing_count == count


def test_component_full_emit(
    component: ProgrammedPeriodicComponent,
    state: ProgrammedPeriodicState,
):
    # given
    state, _ = component.use(None, state)
    state, events = component.elapse(5_000, state)

    # then
    dealing_count = sum([e.tag == Tag.DAMAGE for e in events])
    assert dealing_count == 15
