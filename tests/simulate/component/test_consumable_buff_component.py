# pylint: disable=W0621
import pytest

from simaple.core import Stat
from simaple.simulate.component.common.consumable_buff_skill import (
    ConsumableBuffSkillComponent,
    ConsumableBuffSkillState,
)
from simaple.simulate.global_property import Dynamics
from tests.simulate.component.util import is_rejected


@pytest.fixture
def consumable_buff_component():
    return ConsumableBuffSkillComponent(
        id="test",
        name="consumable-buff-component",
        stat=Stat(attack_power=30),
        delay=600,
        cooldown_duration=30_000,
        lasting_duration=15_000,
        maximum_stack=2,
    )


@pytest.fixture
def consumable_buff_state(
    consumable_buff_component: ConsumableBuffSkillComponent, dynamics: Dynamics
):
    return ConsumableBuffSkillState.model_validate(
        {
            **consumable_buff_component.get_default_state(),
            "dynamics": dynamics,
        }
    )


def test_use_consumable_buff_component(
    consumable_buff_component: ConsumableBuffSkillComponent,
    consumable_buff_state: ConsumableBuffSkillState,
):
    state, _ = consumable_buff_component.use(None, consumable_buff_state)
    assert consumable_buff_component.buff(state) == Stat(attack_power=30)


def test_use_consumable_buff_component_remains(
    consumable_buff_component: ConsumableBuffSkillComponent,
    consumable_buff_state: ConsumableBuffSkillState,
):
    state, _ = consumable_buff_component.use(None, consumable_buff_state)
    state, _ = consumable_buff_component.elapse(10_000, state)
    assert consumable_buff_component.buff(state) == Stat(attack_power=30)


def test_use_consumable_buff_component_turns_off(
    consumable_buff_component: ConsumableBuffSkillComponent,
    consumable_buff_state: ConsumableBuffSkillState,
):
    state, _ = consumable_buff_component.use(None, consumable_buff_state)
    state, _ = consumable_buff_component.elapse(20_000, state)
    assert consumable_buff_component.buff(state) is None


def test_use_consumable_buff_component_twice(
    consumable_buff_component: ConsumableBuffSkillComponent,
    consumable_buff_state: ConsumableBuffSkillState,
):
    state, _ = consumable_buff_component.use(None, consumable_buff_state)
    state, events = consumable_buff_component.use(None, state)

    assert not is_rejected(events)
    assert consumable_buff_component.buff(state) == Stat(attack_power=30)


def test_use_consumable_buff_component_interval(
    consumable_buff_component: ConsumableBuffSkillComponent,
    consumable_buff_state: ConsumableBuffSkillState,
):
    state, _ = consumable_buff_component.use(None, consumable_buff_state)
    state, _ = consumable_buff_component.elapse(15_000, state)
    state, _ = consumable_buff_component.use(None, state)
    state, _ = consumable_buff_component.elapse(15_000, state)
    state, events = consumable_buff_component.use(None, state)

    assert not is_rejected(events)
    assert consumable_buff_component.buff(state) == Stat(attack_power=30)


def test_use_consumable_buff_component_long_elapse(
    consumable_buff_component: ConsumableBuffSkillComponent,
    consumable_buff_state: ConsumableBuffSkillState,
):
    state, _ = consumable_buff_component.use(None, consumable_buff_state)
    state, _ = consumable_buff_component.use(None, state)
    state, _ = consumable_buff_component.elapse(60_000, state)
    state, _ = consumable_buff_component.use(None, state)
    state, events = consumable_buff_component.use(None, state)

    assert not is_rejected(events)
    assert consumable_buff_component.buff(state) == Stat(attack_power=30)


def test_use_consumable_buff_component_forbidden(
    consumable_buff_component: ConsumableBuffSkillComponent,
    consumable_buff_state: ConsumableBuffSkillState,
):
    state, _ = consumable_buff_component.use(None, consumable_buff_state)
    state, _ = consumable_buff_component.use(None, state)
    state, events = consumable_buff_component.use(None, state)
    assert is_rejected(events)
