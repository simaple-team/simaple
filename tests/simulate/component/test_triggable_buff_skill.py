# pylint: disable=W0621
import pytest

from simaple.simulate.component.triggable_buff_skill import TriggableBuffSkill
from tests.simulate.component.util import count_damage_skill


@pytest.fixture(name="triggable_buff_skill")
def fixture_triggable_buff_skill(bare_store):
    return TriggableBuffSkill(
        name="test-triggable",
        cooldown=30_000,
        delay=300,
        duration=10_000,
        trigger_cooldown=4_000,
        trigger_damage=100,
        trigger_hit=3,
    ).compile(bare_store)


def test_trigger_emit_damage(triggable_buff_skill):
    triggable_buff_skill.use(None)
    events = triggable_buff_skill.trigger(None)

    assert count_damage_skill(events) == 1


def test_trigger_disabled_after_first_trigger(triggable_buff_skill):
    triggable_buff_skill.use(None)
    triggable_buff_skill.trigger(None)
    triggable_buff_skill.elapse(2_000)

    events = triggable_buff_skill.trigger(None)

    assert count_damage_skill(events) == 0


def test_trigger_enabled_after_first_trigger(triggable_buff_skill):
    triggable_buff_skill.use(None)
    triggable_buff_skill.trigger(None)
    triggable_buff_skill.elapse(4_000)

    events = triggable_buff_skill.trigger(None)

    assert count_damage_skill(events) == 1


def test_trigger_disabled_after_time_done(triggable_buff_skill):
    triggable_buff_skill.use(None)
    triggable_buff_skill.elapse(11_000)

    events = triggable_buff_skill.trigger(None)

    assert count_damage_skill(events) == 0
