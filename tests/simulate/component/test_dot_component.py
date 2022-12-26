# pylint: disable=W0621
import pytest

from simaple.simulate.component.skill import DOTSkillComponent
from simaple.simulate.reserved_names import Tag


@pytest.fixture
def dot_damage_component():
    component = DOTSkillComponent(
        name="DOT-damage-component",
        tick_interval=120,
        tick_damage=50,
        lasting_duration=1_000,
    )
    return component


@pytest.fixture
def compiled_dot_component(dot_damage_component, bare_store):
    return dot_damage_component.compile(bare_store)


def test_dot_damage_component_emit_initial_damage(compiled_dot_component):
    compiled_dot_component.apply(None)
    assert compiled_dot_component.periodic.time_left == 1_000


def test_dot_damage_component_emit_after(compiled_dot_component):
    compiled_dot_component.apply(None)
    events = compiled_dot_component.elapse(120 * 8)

    dealing_count = sum([e.tag == Tag.DAMAGE for e in events])

    assert dealing_count == 8 - 1


def test_dot_damage_component_partial_emit(compiled_dot_component):
    compiled_dot_component.apply(None)
    events = compiled_dot_component.elapse(120 * 8 + 60)

    dealing_count = sum([e.tag == Tag.DAMAGE for e in events])

    assert dealing_count == 8


def test_dot_damage_component_full_emit(compiled_dot_component):
    compiled_dot_component.apply(None)
    events = compiled_dot_component.elapse(120 * 30)

    dealing_count = sum([e.tag == Tag.DAMAGE for e in events])

    assert dealing_count == 8
