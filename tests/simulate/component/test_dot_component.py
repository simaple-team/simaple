# pylint: disable=W0621
import pytest

from simaple.simulate.component.skill import DOTSkillComponent, DOTState
from simaple.simulate.global_property import Dynamics
from simaple.simulate.reserved_names import Tag


@pytest.fixture
def dot_component():
    return DOTSkillComponent(
        name="DOT-damage-component",
        periodic_interval=120,
        periodic_damage=50,
        lasting_duration=1_000,
    )


@pytest.fixture
def dot_state(dot_component: DOTSkillComponent, dynamics: Dynamics):
    return DOTState.parse_obj(
        {**dot_component.get_default_state(), "dynamics": dynamics}
    )


def test_dot_component_emit_initial_damage(
    dot_component: DOTSkillComponent, dot_state: DOTState
):
    # when
    state, _ = dot_component.apply(None, dot_state)

    # then
    assert state.periodic.time_left == 1_000


def test_dot_component_emit_after(
    dot_component: DOTSkillComponent, dot_state: DOTState
):
    # when
    state, _ = dot_component.apply(None, dot_state)
    state, events = dot_component.elapse(120 * 8, state)

    # then
    dealing_count = sum([e.tag == Tag.DAMAGE for e in events])
    assert dealing_count == 8 - 1


def test_dot_component_partial_emit(
    dot_component: DOTSkillComponent, dot_state: DOTState
):
    # when
    state, _ = dot_component.apply(None, dot_state)
    state, events = dot_component.elapse(120 * 8 + 60, state)

    # then
    dealing_count = sum([e.tag == Tag.DAMAGE for e in events])
    assert dealing_count == 8


def test_dot_component_full_emit(dot_component: DOTSkillComponent, dot_state: DOTState):
    # when
    state, _ = dot_component.apply(None, dot_state)
    state, events = dot_component.elapse(120 * 30, state)

    # then
    dealing_count = sum([e.tag == Tag.DAMAGE for e in events])
    assert dealing_count == 8
