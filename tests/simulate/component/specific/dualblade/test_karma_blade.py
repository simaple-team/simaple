import pytest

from simaple.simulate.component.specific.dualblade import (
    KarmaBladeTriggerComponent,
    KarmaBladeTriggerState,
)
from simaple.simulate.global_property import Dynamics
from tests.simulate.component.util import count_damage_skill


@pytest.fixture(name="karma_blade_trigger")
def fixture_karma_blade_trigger():
    return KarmaBladeTriggerComponent(
        id="test",
        name="test-karma-blade-trigger",
        damage=1071,
        hit=8,
        delay=0,
        cooldown_duration=100,
        lasting_duration=20000,
        triggable_count=35,
        finish_hit=210,
        finish_damage=1100,
    )


@pytest.fixture(name="karma_blade_trigger_state")
def fixture_karma_blade_trigger_state(
    karma_blade_trigger: KarmaBladeTriggerComponent, dynamics: Dynamics
):
    return {**karma_blade_trigger.get_default_state(), "dynamics": dynamics}


def test_triggable_count(
    karma_blade_trigger: KarmaBladeTriggerComponent,
    karma_blade_trigger_state: KarmaBladeTriggerState,
):
    """
    triggable_count가 주어졌을 때, 막타를 포함해 triggable_count + 1번의 데미지가 발생한다.
    """
    # given
    state, events = karma_blade_trigger.use(None, karma_blade_trigger_state)

    # when
    total_events = []
    for _ in range(100):
        state, trigger_events = karma_blade_trigger.trigger(None, state)
        state, elapse_events = karma_blade_trigger.elapse(100, state)
        total_events += trigger_events
        total_events += elapse_events

    # then
    assert count_damage_skill(total_events) == 35 + 1


def test_trigger_cooldown(
    karma_blade_trigger: KarmaBladeTriggerComponent,
    karma_blade_trigger_state: KarmaBladeTriggerState,
):
    """
    쿨다운이 지나지 않으면 트리거에서 데미지를 발생시키지 않는다.
    """
    # given
    state, _ = karma_blade_trigger.use(None, karma_blade_trigger_state)
    state, _ = karma_blade_trigger.trigger(None, state)
    state, _ = karma_blade_trigger.elapse(50, state)

    # when
    state, events = karma_blade_trigger.trigger(None, state)

    # then
    assert count_damage_skill(events) == 0


def test_elapse_finish_damage(
    karma_blade_trigger: KarmaBladeTriggerComponent,
    karma_blade_trigger_state: KarmaBladeTriggerState,
):
    """
    스택이 남아있는 상태에서 lasting_duration이 지나면 막타가 발생한다.
    """
    # given
    state, events = karma_blade_trigger.use(None, karma_blade_trigger_state)

    # when
    state, events = karma_blade_trigger.elapse(20000, state)

    # then
    assert count_damage_skill(events) == 1
