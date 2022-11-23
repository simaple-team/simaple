# pylint: disable=W0621
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


@pytest.fixture
def compiled_tick_damage_component(tick_damage_component, bare_store):
    return tick_damage_component.compile(bare_store)


def test_tick_damage_component_emit_initial_damage(
    tick_damage_component, compiled_tick_damage_component
):
    events = compiled_tick_damage_component.use(None)
    assert events[0].payload == {"damage": 100, "hit": 1.0}
    assert events[1].payload == {"time": 30.0}


def test_tick_damage_component_emit_after(compiled_tick_damage_component):
    compiled_tick_damage_component.use(None)
    events = compiled_tick_damage_component.elapse(120 * 8)

    dealing_count = sum([e.tag == Tag.DAMAGE for e in events])

    assert dealing_count == 8 - 1


def test_tick_damage_component_partial_emit(compiled_tick_damage_component):
    compiled_tick_damage_component.use(None)
    events = compiled_tick_damage_component.elapse(120 * 8 + 60)

    dealing_count = sum([e.tag == Tag.DAMAGE for e in events])

    assert dealing_count == 8


def test_tick_damage_component_full_emit(compiled_tick_damage_component):
    compiled_tick_damage_component.use(None)
    events = compiled_tick_damage_component.elapse(120 * 30)

    dealing_count = sum([e.tag == Tag.DAMAGE for e in events])

    assert dealing_count == 8
