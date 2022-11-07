import pytest

from simaple.simulate.component.skill import DOTSkillComponent
from simaple.simulate.reserved_names import Tag


@pytest.fixture
def dot_damage_component():
    component = DOTSkillComponent(
        name="DOT-damage-component",
        tick_interval=120,
        tick_damage=50,
        duration=1_000,
    )
    return component


def test_dot_damage_component_emit_initial_damage(dot_damage_component):
    default_state = dot_damage_component.get_default_state()
    interval_state = default_state.get("interval_state")

    interval_state, events = dot_damage_component.apply(None, interval_state)

    assert interval_state.interval_time_left == 1_000


def test_dot_damage_component_emit_after(dot_damage_component):
    default_state = dot_damage_component.get_default_state()
    interval_state = default_state.get("interval_state")

    interval_state, _ = dot_damage_component.apply(None, interval_state)

    states, events = dot_damage_component.elapse(120 * 8, interval_state)

    dealing_count = sum([e.tag == Tag.DAMAGE for e in events])

    assert dealing_count == 8 - 1


def test_dot_damage_component_partial_emit(dot_damage_component):
    default_state = dot_damage_component.get_default_state()
    interval_state = default_state.get("interval_state")

    interval_state, _ = dot_damage_component.apply(None, interval_state)

    states, events = dot_damage_component.elapse(120 * 8 + 60, interval_state)

    dealing_count = sum([e.tag == Tag.DAMAGE for e in events])

    assert dealing_count == 8


def test_dot_damage_component_full_emit(dot_damage_component):
    default_state = dot_damage_component.get_default_state()
    interval_state = default_state.get("interval_state")

    interval_state, _ = dot_damage_component.apply(None, interval_state)

    states, events = dot_damage_component.elapse(120 * 30, interval_state)

    dealing_count = sum([e.tag == Tag.DAMAGE for e in events])

    assert dealing_count == 8
