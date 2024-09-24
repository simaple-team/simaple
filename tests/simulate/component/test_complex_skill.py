# pylint: disable=W0621
import pytest

from simaple.simulate.component.complex_skill import (
    AttackSkillIncludeReforged,
    AttackSkillIncludeReforgedState,
)
from simaple.simulate.global_property import Dynamics
from tests.simulate.component.util import compute_total_damage_coefficient


@pytest.fixture
def attack_skill_include_reforgedskill():
    component = AttackSkillIncludeReforged(
        id="test",
        name="component",
        damage=200,
        hit=3.0,
        delay=30,
        cooldown_duration=0,
        reforged_damage=1000,
        reforged_hit=3.0,
        reforge_cooldown_duration=7_000,
        reforged_multiple=2,
    )
    return component


@pytest.fixture
def attack_skill_include_reforgedskill_state(
    attack_skill_include_reforgedskill: AttackSkillIncludeReforged,
    dynamics: Dynamics,
):
    return AttackSkillIncludeReforgedState.model_validate(
        {
            **attack_skill_include_reforgedskill.get_default_state(),
            "dynamics": dynamics,
        }
    )


def test_attack_skill_include_reforgedskill(
    attack_skill_include_reforgedskill: AttackSkillIncludeReforged,
    attack_skill_include_reforgedskill_state: AttackSkillIncludeReforgedState,
):
    # given
    (
        attack_skill_include_reforgedskill_state,
        events,
    ) = attack_skill_include_reforgedskill.use(None, attack_skill_include_reforgedskill_state)
    assert compute_total_damage_coefficient(events) == 6000

    (
        attack_skill_include_reforgedskill_state,
        events,
    ) = attack_skill_include_reforgedskill.use(None, attack_skill_include_reforgedskill_state)
    assert compute_total_damage_coefficient(events) == 600

    (
        attack_skill_include_reforgedskill_state,
        events,
    ) = attack_skill_include_reforgedskill.elapse(5_000, attack_skill_include_reforgedskill_state)

    (
        attack_skill_include_reforgedskill_state,
        events,
    ) = attack_skill_include_reforgedskill.use(None, attack_skill_include_reforgedskill_state)
    assert compute_total_damage_coefficient(events) == 600

    (
        attack_skill_include_reforgedskill_state,
        events,
    ) = attack_skill_include_reforgedskill.elapse(2_000, attack_skill_include_reforgedskill_state)

    (
        attack_skill_include_reforgedskill_state,
        events,
    ) = attack_skill_include_reforgedskill.use(None, attack_skill_include_reforgedskill_state)
    assert compute_total_damage_coefficient(events) == 6000
