# pylint: disable=W0621
import pytest

from simaple.simulate.component.common.temporal_enhancing_attack_skill import (
    TemporalEnhancingAttackSkill,
    TemporalEnhancingAttackSkillState,
)
from simaple.simulate.global_property import Dynamics
from tests.simulate.component.util import compute_total_damage_coefficient


@pytest.fixture
def temporal_enhancing_attack_skill():
    component = TemporalEnhancingAttackSkill(
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
def temporal_enhancing_attack_skill_state(
    temporal_enhancing_attack_skill: TemporalEnhancingAttackSkill,
    dynamics: Dynamics,
):
    return {
        **temporal_enhancing_attack_skill.get_default_state(),
        "dynamics": dynamics,
    }


def test_temporal_enhancing_attack_skill(
    temporal_enhancing_attack_skill: TemporalEnhancingAttackSkill,
    temporal_enhancing_attack_skill_state: TemporalEnhancingAttackSkillState,
):
    # given
    (
        temporal_enhancing_attack_skill_state,
        events,
    ) = temporal_enhancing_attack_skill.use(None, temporal_enhancing_attack_skill_state)
    assert compute_total_damage_coefficient(events) == 6000

    (
        temporal_enhancing_attack_skill_state,
        events,
    ) = temporal_enhancing_attack_skill.use(None, temporal_enhancing_attack_skill_state)
    assert compute_total_damage_coefficient(events) == 600

    (
        temporal_enhancing_attack_skill_state,
        events,
    ) = temporal_enhancing_attack_skill.elapse(
        5_000, temporal_enhancing_attack_skill_state
    )

    (
        temporal_enhancing_attack_skill_state,
        events,
    ) = temporal_enhancing_attack_skill.use(None, temporal_enhancing_attack_skill_state)
    assert compute_total_damage_coefficient(events) == 600

    (
        temporal_enhancing_attack_skill_state,
        events,
    ) = temporal_enhancing_attack_skill.elapse(
        2_000, temporal_enhancing_attack_skill_state
    )

    (
        temporal_enhancing_attack_skill_state,
        events,
    ) = temporal_enhancing_attack_skill.use(None, temporal_enhancing_attack_skill_state)
    assert compute_total_damage_coefficient(events) == 6000
