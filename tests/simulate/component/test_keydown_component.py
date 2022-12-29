# pylint: disable=W0621
import pytest

from simaple.simulate.component.keydown_skill import (
    KeydownSkillComponent,
    KeydownSkillState,
)
from simaple.simulate.global_property import Dynamics
from tests.simulate.component.util import is_rejected


@pytest.fixture
def keydown_delay():
    return 300


@pytest.fixture
def keydown_component(keydown_delay: float):
    return KeydownSkillComponent(
        name="test-keydown",
        damage=100,
        hit=3,
        cooldown_duration=60_000,
        delay=keydown_delay,
        keydown_end_delay=500,
        finish_damage=500,
        finish_hit=15,
        maximum_keydown_time=keydown_delay * 10,
    )


@pytest.fixture
def keydown_state(keydown_component: KeydownSkillComponent, dynamics: Dynamics):
    return KeydownSkillState.parse_obj(
        {
            **keydown_component.get_default_state(),
            "dynamics": dynamics,
        }
    )


def test_reject(
    keydown_component: KeydownSkillComponent, keydown_state: KeydownSkillState
):
    # when
    state, _ = keydown_component.use(None, keydown_state)
    state, _ = keydown_component.elapse(10_000, state)
    state, events = keydown_component.use(None, state)

    # then
    assert is_rejected(events)


def test_use_keydown_component(
    keydown_component: KeydownSkillComponent, keydown_state: KeydownSkillState
):
    # when
    state, _ = keydown_component.use(None, keydown_state)

    # then
    assert state.keydown.is_running()


def test_use_keydown_component_and_elapse_time(
    keydown_component: KeydownSkillComponent,
    keydown_state: KeydownSkillState,
    keydown_delay: float,
):
    # when
    state, _ = keydown_component.use(None, keydown_state)
    state, _ = keydown_component.elapse(keydown_delay, state)

    # then
    assert state.keydown.is_running()


def test_use_keydown_component_and_elapse_more_time(
    keydown_component: KeydownSkillComponent,
    keydown_state: KeydownSkillState,
    keydown_delay: float,
):
    # when
    state, _ = keydown_component.use(None, keydown_state)
    state, events = keydown_component.elapse(keydown_delay + 10, state)

    # then
    assert not state.keydown.is_running()
    assert events[-1].payload["time"] == 500 - 10 - keydown_delay


def test_use_keydown_component_many_time(
    keydown_component: KeydownSkillComponent,
    keydown_state: KeydownSkillState,
    keydown_delay: float,
):
    # when
    state = keydown_state
    for _ in range(6):
        state, _ = keydown_component.use(None, state)
        state, _ = keydown_component.elapse(keydown_delay, state)

    # then
    assert state.keydown.is_running()


def test_use_keydown_component_too_long(
    keydown_component: KeydownSkillComponent,
    keydown_state: KeydownSkillState,
    keydown_delay: float,
):
    # when
    state = keydown_state
    for _ in range(11):
        state, _ = keydown_component.use(None, state)
        state, _ = keydown_component.elapse(keydown_delay, state)

    # then
    assert not state.keydown.is_running()
