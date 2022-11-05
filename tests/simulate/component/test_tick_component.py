import pytest

from simaple.simulate.component.skill import TickDamageConfiguratedAttackSkillComponent
from simaple.simulate.reserved_names import Tag


@pytest.fixture
def tick_damage_component():
    component = TickDamageConfiguratedAttackSkillComponent(
        name="tick-damage-component",
        damage=100,
        hit=1,
        delay=30,
        tick_interval=120,
        tick_damage=50,
        tick_hit=3,
        duration=1_000,
    )
    return component


def test_tick_damage_component_emit_initial_damage(tick_damage_component):
    default_state = tick_damage_component.get_default_state()
    cooldown_state = default_state.get("cooldown_state")
    interval_state = default_state.get("interval_state")

    states, events = tick_damage_component.use(None, cooldown_state, interval_state)

    assert events == [
        tick_damage_component.event_provider.dealt(100.0, 1.0),
        tick_damage_component.event_provider.delayed(30.0),
    ]


def test_tick_damage_component_emit_after(tick_damage_component):
    default_state = tick_damage_component.get_default_state()
    cooldown_state = default_state.get("cooldown_state")
    interval_state = default_state.get("interval_state")

    (cooldown_state, interval_state), _ = tick_damage_component.use(
        None, cooldown_state, interval_state
    )

    states, events = tick_damage_component.elapse(
        120 * 8, cooldown_state, interval_state
    )

    dealing_count = sum([e.tag == Tag.DAMAGE for e in events])

    assert dealing_count == 8 - 1


def test_tick_damage_component_partial_emit(tick_damage_component):
    default_state = tick_damage_component.get_default_state()
    cooldown_state = default_state.get("cooldown_state")
    interval_state = default_state.get("interval_state")

    (cooldown_state, interval_state), _ = tick_damage_component.use(
        None, cooldown_state, interval_state
    )

    states, events = tick_damage_component.elapse(
        120 * 8 + 60, cooldown_state, interval_state
    )

    dealing_count = sum([e.tag == Tag.DAMAGE for e in events])

    assert dealing_count == 8


def test_tick_damage_component_full_emit(tick_damage_component):
    default_state = tick_damage_component.get_default_state()
    cooldown_state = default_state.get("cooldown_state")
    interval_state = default_state.get("interval_state")

    (cooldown_state, interval_state), _ = tick_damage_component.use(
        None, cooldown_state, interval_state
    )

    states, events = tick_damage_component.elapse(
        120 * 30, cooldown_state, interval_state
    )

    dealing_count = sum([e.tag == Tag.DAMAGE for e in events])

    assert dealing_count == 8
