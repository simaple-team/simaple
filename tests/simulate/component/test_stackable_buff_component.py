# pylint: disable=W0621
import pytest

from simaple.core import Stat
from simaple.simulate.component.skill import (
    StackableBuffSkillComponent,
    StackableBuffSkillState,
)
from simaple.simulate.global_property import Dynamics


@pytest.fixture
def buff_component():
    return StackableBuffSkillComponent(
        id="test",
        name="buff-component",
        stat=Stat(attack_power=30),
        cooldown_duration=30_000,
        delay=600,
        lasting_duration=15_000,
        maximum_stack=2,
    )


@pytest.fixture
def buff_state(buff_component: StackableBuffSkillComponent, dynamics: Dynamics):
    return StackableBuffSkillState.model_validate(
        {**buff_component.get_default_state(), "dynamics": dynamics}
    )


def test_use_buff_component(
    buff_component: StackableBuffSkillComponent, buff_state: StackableBuffSkillState
):
    # when
    state, _ = buff_component.use(None, buff_state)

    # then
    assert buff_component.buff(state) == Stat(attack_power=30)


def test_use_buff_component_twice(
    buff_component: StackableBuffSkillComponent, buff_state: StackableBuffSkillState
):
    # when
    state, _ = buff_component.use(None, buff_state)
    state, _ = buff_component.use(None, state)

    # then
    assert buff_component.buff(state) == Stat(attack_power=60)


def test_use_buff_component_remains(
    buff_component: StackableBuffSkillComponent, buff_state: StackableBuffSkillState
):
    # when
    state, _ = buff_component.use(None, buff_state)
    state, _ = buff_component.elapse(10_000, state)

    # then
    assert buff_component.buff(state) == Stat(attack_power=30)


def test_use_buff_component_turns_off(
    buff_component: StackableBuffSkillComponent, buff_state: StackableBuffSkillState
):
    # when
    state, _ = buff_component.use(None, buff_state)
    state, _ = buff_component.elapse(20_000, state)

    # then
    assert buff_component.buff(state) is None


def test_buff_skill_use_forbidden(
    buff_component: StackableBuffSkillComponent, buff_state: StackableBuffSkillState
):
    # when
    state, _ = buff_component.use(None, buff_state)
    state, _ = buff_component.elapse(20_000, state)
    state, _ = buff_component.use(None, state)

    # then
    assert buff_component.buff(state) is None
