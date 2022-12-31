# pylint: disable=W0621
import pytest

from simaple.core.base import Stat
from simaple.simulate.component.triggable_buff_skill import (
    TriggableBuffSkill,
    TriggableBuffState,
)
from simaple.simulate.global_property import Dynamics
from tests.simulate.component.util import count_damage_skill


@pytest.fixture(name="triggable_buff_skill")
def fixture_triggable_buff_skill():
    return TriggableBuffSkill(
        name="test-triggable",
        cooldown_duration=30_000,
        delay=300,
        lasting_duration=10_000,
        trigger_cooldown_duration=4_000,
        trigger_damage=100,
        trigger_hit=3,
        stat=Stat(attack_power=30),
    )


@pytest.fixture
def triggable_buff_state(triggable_buff_skill: TriggableBuffSkill, dynamics: Dynamics):
    return TriggableBuffState.parse_obj(
        {**triggable_buff_skill.get_default_state(), "dynamics": dynamics}
    )


def test_trigger_emit_damage(
    triggable_buff_skill: TriggableBuffSkill,
    triggable_buff_state: TriggableBuffState,
):
    # given
    state, _ = triggable_buff_skill.use(None, triggable_buff_state)

    # when
    state, events = triggable_buff_skill.trigger(None, state)

    # then
    assert count_damage_skill(events) == 1


def test_trigger_disabled_after_first_trigger(
    triggable_buff_skill: TriggableBuffSkill,
    triggable_buff_state: TriggableBuffState,
):
    # given
    state, _ = triggable_buff_skill.use(None, triggable_buff_state)
    state, _ = triggable_buff_skill.trigger(None, state)
    state, _ = triggable_buff_skill.elapse(2_000, state)

    # when
    state, events = triggable_buff_skill.trigger(None, state)

    # then
    assert count_damage_skill(events) == 0


def test_trigger_enabled_after_first_trigger(
    triggable_buff_skill: TriggableBuffSkill,
    triggable_buff_state: TriggableBuffState,
):
    # given
    state, _ = triggable_buff_skill.use(None, triggable_buff_state)
    state, _ = triggable_buff_skill.trigger(None, state)
    state, _ = triggable_buff_skill.elapse(4_000, state)

    # when
    state, events = triggable_buff_skill.trigger(None, state)

    # then
    assert count_damage_skill(events) == 1


def test_trigger_disabled_after_time_done(
    triggable_buff_skill: TriggableBuffSkill,
    triggable_buff_state: TriggableBuffState,
):
    # given
    state, _ = triggable_buff_skill.use(None, triggable_buff_state)
    state, _ = triggable_buff_skill.elapse(11_000, state)

    # when
    state, events = triggable_buff_skill.trigger(None, state)

    # then
    assert count_damage_skill(events) == 0


def test_trigger_buff_remains(
    triggable_buff_skill: TriggableBuffSkill,
    triggable_buff_state: TriggableBuffState,
):
    # given
    state, _ = triggable_buff_skill.use(None, triggable_buff_state)

    # when
    state, _ = triggable_buff_skill.elapse(4_000, state)

    # then
    assert triggable_buff_skill.buff(state) == Stat(attack_power=30)


def test_trigger_buff_turns_off(
    triggable_buff_skill: TriggableBuffSkill,
    triggable_buff_state: TriggableBuffState,
):
    # given
    state, _ = triggable_buff_skill.use(None, triggable_buff_state)

    # when
    state, _ = triggable_buff_skill.elapse(11_000, state)

    # then
    assert triggable_buff_skill.buff(state) is None
