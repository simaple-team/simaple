# pylint: disable=W0621
import pytest

from simaple.simulate.component.common.keydown_skill import (
    KeydownSkillComponent,
    KeydownSkillState,
)
from simaple.simulate.global_property import Dynamics
from simaple.simulate.reserved_names import Tag
from tests.simulate.component.util import count_damage_skill, is_rejected, total_delay


@pytest.fixture(name="keydown_fixture", params=[300, 500, 800])
def keydown_fixture(request, dynamics: Dynamics):
    delay: float = request.param
    component = KeydownSkillComponent(
        id="test",
        name="test-keydown",
        damage=100,
        hit=3,
        cooldown_duration=60_000,
        delay=delay,
        maximum_keydown_time=delay * 10,
        keydown_prepare_delay=delay * 2,
        keydown_end_delay=500,
        finish_damage=500,
        finish_hit=15,
    )
    state = KeydownSkillState.model_validate(
        {
            **component.get_default_state(),
            "dynamics": dynamics,
        }
    )
    return (component, state, delay)


def test_use_reject(
    keydown_fixture: tuple[KeydownSkillComponent, KeydownSkillState, float],
):
    # given
    component, state, _ = keydown_fixture

    # when
    state, _ = component.use(None, state)
    state, _ = component.elapse(10_000, state)
    state, events = component.use(None, state)

    # then
    assert is_rejected(events)


def test_stop_reject(
    keydown_fixture: tuple[KeydownSkillComponent, KeydownSkillState, float],
):
    # given
    component, state, _ = keydown_fixture

    # when
    state, events = component.stop(None, state)

    # then
    assert is_rejected(events)


def test_use(keydown_fixture: tuple[KeydownSkillComponent, KeydownSkillState, float]):
    # given
    component, state, _ = keydown_fixture

    # when
    state, _ = component.use(None, state)

    # then
    assert state.keydown.running is True


def test_use_and_stop(
    keydown_fixture: tuple[KeydownSkillComponent, KeydownSkillState, float],
):
    # given
    component, state, _ = keydown_fixture

    # when
    state, _ = component.use(None, state)
    state, events = component.stop(None, state)

    # then
    damage_events = [e for e in events if e["tag"] == Tag.DAMAGE]
    assert damage_events[-1]["payload"]["damage"] == component.finish_damage
    assert damage_events[-1]["payload"]["hit"] == component.finish_hit
    assert total_delay(events) == component.keydown_end_delay
    assert state.keydown.running is False


def test_use_and_elapse_lesser_than_prepare_delay(
    keydown_fixture: tuple[KeydownSkillComponent, KeydownSkillState, float],
):
    # given
    component, state, delay = keydown_fixture
    to_elapse = delay * 2 - 10

    # when
    state, _ = component.use(None, state)
    state, events = component.elapse(to_elapse, state)

    # then
    assert count_damage_skill(events) == 0
    assert total_delay(events) == 10


def test_use_and_elapse_equals_prepare_delay(
    keydown_fixture: tuple[KeydownSkillComponent, KeydownSkillState, float],
):
    # given
    component, state, delay = keydown_fixture
    to_elapse = delay * 2

    # when
    state, _ = component.use(None, state)
    state, events = component.elapse(to_elapse, state)

    # then
    assert count_damage_skill(events) == 1
    assert total_delay(events) == delay


def test_use_and_elapse_greater_than_prepare_delay(
    keydown_fixture: tuple[KeydownSkillComponent, KeydownSkillState, float],
):
    # given
    component, state, delay = keydown_fixture
    to_elapse = delay * 2 + 10

    # when
    state, _ = component.use(None, state)
    state, events = component.elapse(to_elapse, state)

    # then
    assert count_damage_skill(events) == 1
    assert total_delay(events) == delay - 10


def test_elapse_until_finish(
    keydown_fixture: tuple[KeydownSkillComponent, KeydownSkillState, float],
):
    # given
    component, state, delay = keydown_fixture

    # when
    state, _ = component.use(None, state)
    state, elapse_events = component.elapse(delay * 10, state)

    # then
    damage_events = [e for e in elapse_events if e["tag"] == Tag.DAMAGE]
    assert damage_events[-1]["payload"]["damage"] == component.finish_damage
    assert damage_events[-1]["payload"]["hit"] == component.finish_hit
    assert total_delay(elapse_events) == component.keydown_end_delay
    assert state.keydown.running is False


def test_elapse_during_finish_delay(
    keydown_fixture: tuple[KeydownSkillComponent, KeydownSkillState, float],
):
    # given
    component, state, delay = keydown_fixture

    # when
    state, _ = component.use(None, state)
    state, elapse_events = component.elapse(delay * 10 + 10, state)

    # then
    damage_events = [e for e in elapse_events if e["tag"] == Tag.DAMAGE]
    assert damage_events[-1]["payload"]["damage"] == component.finish_damage
    assert damage_events[-1]["payload"]["hit"] == component.finish_hit
    assert total_delay(elapse_events) == component.keydown_end_delay - 10
    assert state.keydown.running is False


def test_elapse_just_before_finish(
    keydown_fixture: tuple[KeydownSkillComponent, KeydownSkillState, float],
):
    # given
    component, state, delay = keydown_fixture

    # when
    state, _ = component.use(None, state)
    state, _ = component.elapse(delay * 10 - 10, state)

    # then
    assert state.keydown.running is True


def test_elapse_very_long(
    keydown_fixture: tuple[KeydownSkillComponent, KeydownSkillState, float],
):
    # given
    component, state, delay = keydown_fixture

    # when
    state, _ = component.use(None, state)
    state, elapse_events = component.elapse(delay * 20, state)

    # then
    damage_events = [e for e in elapse_events if e["tag"] == Tag.DAMAGE]
    assert damage_events[-1]["payload"]["damage"] == component.finish_damage
    assert damage_events[-1]["payload"]["hit"] == component.finish_hit
    assert total_delay(elapse_events) == 0
    assert state.keydown.running is False
