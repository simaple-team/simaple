# pylint: disable=W0621
import pytest

from simaple.simulate.component.skill import (
    PeriodicDamageConfiguratedAttackSkillComponent,
)
from simaple.simulate.reserved_names import Tag


@pytest.fixture
def periodic_damage_component():
    component = PeriodicDamageConfiguratedAttackSkillComponent(
        name="periodic-damage-component",
        damage=100,
        hit=1,
        delay=30,
        periodic_interval=120,
        periodic_damage=50,
        periodic_hit=3,
        lasting_duration=1_000,
        cooldown_duration=30_000,
    )
    return component


@pytest.fixture
def compiled_periodic_damage_component(periodic_damage_component, bare_store):
    return periodic_damage_component.compile(bare_store)


def test_periodic_damage_component_reject(compiled_periodic_damage_component):
    events = compiled_periodic_damage_component.use(None)
    events = compiled_periodic_damage_component.use(None)

    assert events[0].tag == Tag.REJECT


def test_periodic_damage_component_emit_initial_damage(
    compiled_periodic_damage_component,
):
    events = compiled_periodic_damage_component.use(None)
    assert events[0].payload == {"damage": 100, "hit": 1.0, "modifier": None}
    assert events[1].payload == {"time": 30.0}


def test_periodic_damage_component_emit_after(compiled_periodic_damage_component):
    compiled_periodic_damage_component.use(None)
    events = compiled_periodic_damage_component.elapse(120 * 8)

    dealing_count = sum([e.tag == Tag.DAMAGE for e in events])

    assert dealing_count == 8 - 1


def test_periodic_damage_component_partial_emit(compiled_periodic_damage_component):
    compiled_periodic_damage_component.use(None)
    events = compiled_periodic_damage_component.elapse(120 * 8 + 60)

    dealing_count = sum([e.tag == Tag.DAMAGE for e in events])

    assert dealing_count == 8


def test_periodic_damage_component_full_emit(compiled_periodic_damage_component):
    compiled_periodic_damage_component.use(None)
    events = compiled_periodic_damage_component.elapse(120 * 30)

    dealing_count = sum([e.tag == Tag.DAMAGE for e in events])

    assert dealing_count == 8
