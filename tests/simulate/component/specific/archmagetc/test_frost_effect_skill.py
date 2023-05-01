# pylint: disable=W0621
import pytest

from simaple.core.base import Stat
from simaple.simulate.component.entity import Periodic, Stack
from simaple.simulate.component.specific.archmagetc import (
    FrostEffect,
    FrostEffectState,
    ThunderAttackSkillComponent,
    ThunderAttackSkillState,
)
from simaple.simulate.global_property import Dynamics
from simaple.simulate.reserved_names import Tag


@pytest.fixture(name="thunder_attack_skill")
def fixture_thunder_attack_skill():
    return ThunderAttackSkillComponent(
        id="test",
        name="test-component",
        damage=130,
        delay=500,
        hit=3,
        cooldown_duration=0,
    )


@pytest.fixture(name="thunder_attack_skill_state")
def thunder_attack_skill_state(
    thunder_attack_skill: ThunderAttackSkillComponent,
    dynamics: Dynamics,
    frost_effect_state: FrostEffectState,
    jupyter_thunder_periodic: Periodic,
):
    return ThunderAttackSkillState.parse_obj(
        {
            **thunder_attack_skill.get_default_state(),
            "dynamics": dynamics,
            "frost_stack": frost_effect_state.frost_stack,
            "jupyter_thunder_shock": jupyter_thunder_periodic,
        }
    )


def test_frost_effect_reducer(
    frost_effect: FrostEffect, frost_effect_state: FrostEffectState
):
    # when
    state, _ = frost_effect.increase_step(None, frost_effect_state)

    # then
    assert frost_effect.buff(state) == Stat(critical_damage=3)


def test_with_no_stack(
    thunder_attack_skill: ThunderAttackSkillComponent,
    thunder_attack_skill_state: ThunderAttackSkillState,
):
    # when
    _, events = thunder_attack_skill.use(None, thunder_attack_skill_state)
    damage_events = [e for e in events if e.tag == Tag.DAMAGE]

    # then
    assert damage_events[0].payload["modifier"] == Stat()


def test_with_some_stack(
    thunder_attack_skill: ThunderAttackSkillComponent,
    thunder_attack_skill_state: ThunderAttackSkillState,
):
    # given
    thunder_attack_skill_state.frost_stack = Stack(
        maximum_stack=5,
        stack=3,
    )

    # when
    state, events = thunder_attack_skill.use(None, thunder_attack_skill_state)

    # then
    damage_events = [e for e in events if e.tag == Tag.DAMAGE]
    assert damage_events[0].payload["modifier"] == Stat(damage_multiplier=12 * 3)
