# pylint: disable=W0621
import pytest

from simaple.simulate.component.common.periodic_damage_configurated_attack_skill import (
    PeriodicDamageConfiguratedAttackSkillComponent,
    PeriodicDamageState,
)
from simaple.simulate.global_property import Dynamics
from simaple.simulate.reserved_names import Tag


@pytest.fixture
def periodic_damage_component():
    component = PeriodicDamageConfiguratedAttackSkillComponent(
        id="test",
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
def periodic_damage_state(
    periodic_damage_component: PeriodicDamageConfiguratedAttackSkillComponent,
    dynamics: Dynamics,
):
    return PeriodicDamageState.model_validate(
        {
            **periodic_damage_component.get_default_state(),
            "dynamics": dynamics,
        }
    )


def test_periodic_damage_component_reject(
    periodic_damage_component: PeriodicDamageConfiguratedAttackSkillComponent,
    periodic_damage_state: PeriodicDamageState,
):
    # given
    state, events = periodic_damage_component.use(None, periodic_damage_state)
    state, events = periodic_damage_component.use(None, state)

    # then
    assert events[0]["tag"] == Tag.REJECT


def test_periodic_damage_component_emit_initial_damage(
    periodic_damage_component: PeriodicDamageConfiguratedAttackSkillComponent,
    periodic_damage_state: PeriodicDamageState,
):
    # given
    _, events = periodic_damage_component.use(None, periodic_damage_state)

    # then
    assert events[0]["payload"] == {"damage": 100, "hit": 1.0, "modifier": None}
    assert events[1]["payload"] == {"time": 30.0}


def test_periodic_damage_component_emit_after(
    periodic_damage_component: PeriodicDamageConfiguratedAttackSkillComponent,
    periodic_damage_state: PeriodicDamageState,
):
    # given
    state, _ = periodic_damage_component.use(None, periodic_damage_state)
    state, events = periodic_damage_component.elapse(120 * 8, state)

    # then
    dealing_count = sum([e["tag"] == Tag.DAMAGE for e in events])
    assert dealing_count == 8 - 1


def test_periodic_damage_component_partial_emit(
    periodic_damage_component: PeriodicDamageConfiguratedAttackSkillComponent,
    periodic_damage_state: PeriodicDamageState,
):
    # given
    state, _ = periodic_damage_component.use(None, periodic_damage_state)
    state, events = periodic_damage_component.elapse(120 * 8 + 60, state)

    # then
    dealing_count = sum([e["tag"] == Tag.DAMAGE for e in events])
    assert dealing_count == 8


def test_periodic_damage_component_full_emit(
    periodic_damage_component: PeriodicDamageConfiguratedAttackSkillComponent,
    periodic_damage_state: PeriodicDamageState,
):
    # given
    state, _ = periodic_damage_component.use(None, periodic_damage_state)
    state, events = periodic_damage_component.elapse(120 * 30, state)

    # then
    dealing_count = sum([e["tag"] == Tag.DAMAGE for e in events])
    assert dealing_count == 8
