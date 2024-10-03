# pylint: disable=W0621
import pytest

from simaple.core import Stat
from simaple.simulate.component.common.buff_skill import (
    BuffSkillComponent,
    BuffSkillState,
)
from simaple.simulate.global_property import Dynamics


@pytest.fixture
def buff_component():
    return BuffSkillComponent(
        id="test",
        name="buff-component",
        stat=Stat(attack_power=30),
        cooldown_duration=30_000,
        delay=600,
        lasting_duration=15_000,
    )


@pytest.fixture
def buff_state(buff_component: BuffSkillComponent, dynamics: Dynamics):
    return BuffSkillState.model_validate(
        {**buff_component.get_default_state(), "dynamics": dynamics}
    )


def test_use_buff_component(
    buff_component: BuffSkillComponent, buff_state: BuffSkillState
):
    # when
    state, _ = buff_component.use(None, buff_state)

    # then
    assert buff_component.buff(state) == Stat(attack_power=30)


def test_use_buff_component_remains(
    buff_component: BuffSkillComponent, buff_state: BuffSkillState
):
    # when
    state, _ = buff_component.use(None, buff_state)
    state, _ = buff_component.elapse(10_000, state)

    # then
    assert buff_component.buff(state) == Stat(attack_power=30)


def test_use_buff_component_turns_off(
    buff_component: BuffSkillComponent, buff_state: BuffSkillState
):
    # when
    state, _ = buff_component.use(None, buff_state)
    state, _ = buff_component.elapse(20_000, state)

    # then
    assert buff_component.buff(state) is None


def test_buff_skill_use_forbidden(
    buff_component: BuffSkillComponent, buff_state: BuffSkillState
):
    # when
    state, _ = buff_component.use(None, buff_state)
    state, _ = buff_component.elapse(20_000, state)
    state, _ = buff_component.use(None, state)

    # then
    assert buff_component.buff(state) is None
