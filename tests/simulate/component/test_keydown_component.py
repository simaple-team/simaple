# pylint: disable=W0621
import pytest

from simaple.simulate.component.keydown_skill import KeydownSkillComponent
from tests.simulate.component.util import is_rejected


@pytest.fixture
def keydown_delay():
    return 300


@pytest.fixture
def keydown_component(bare_store, keydown_delay):
    return KeydownSkillComponent(
        name="test-keydown",
        damage=100,
        hit=3,
        cooldown=60_000,
        delay=keydown_delay,
        keydown_end_delay=500,
        finish_damage=500,
        finish_hit=15,
        maximum_keydown_time=keydown_delay * 10,
    ).compile(bare_store)


def test_reject(keydown_component):
    keydown_component.use(None)
    keydown_component.elapse(10_000)
    events = keydown_component.use(None)

    assert is_rejected(events)


def test_use_keydown_component(keydown_component):
    keydown_component.use(None)
    assert keydown_component.keydown_state.is_running()


def test_use_keydown_component_and_elapse_time(keydown_component, keydown_delay):
    keydown_component.use(None)
    keydown_component.elapse(keydown_delay)
    assert keydown_component.keydown_state.is_running()


def test_use_keydown_component_and_elapse_more_time(keydown_component, keydown_delay):
    keydown_component.use(None)
    events = keydown_component.elapse(keydown_delay + 10)
    assert not keydown_component.keydown_state.is_running()
    assert events[-1].payload["time"] == 500 - 10 - keydown_delay


def test_use_keydown_component_many_time(keydown_component, keydown_delay):
    for _ in range(6):
        keydown_component.use(None)
        keydown_component.elapse(keydown_delay)
    assert keydown_component.keydown_state.is_running()


def test_use_keydown_component_too_long(keydown_component, keydown_delay):
    for _ in range(11):
        keydown_component.use(None)
        keydown_component.elapse(keydown_delay)

    assert not keydown_component.keydown_state.is_running()
