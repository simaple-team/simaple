import pytest
import yaml

from simaple.container.simulation import SimulationEnvironment
from simaple.wasm.workspace import (
    hasEnvironment,
    provideEnvironmentAugmentedPlan,
    runPlan,
)


def test_has_environment_returns_false_without_environment():
    plan = """
author: "Alice"
provider:
    name: "BaselineEnvironmentProvider"
    data:
        tier: Legendary
        jobtype: archmagetc
        level: 270
        artifact_level: 40
        passive_skill_level: 0
        combat_orders_level: 1
---
ELAPSE 10.0
ELAPSE 10.0
ELAPSE 10.0
ELAPSE 10.0
    """

    assert not hasEnvironment(plan)


def test_has_environment_returns_true_with_environment():
    plan = """
author: "Alice"
provider:
    name: "BaselineEnvironmentProvider"
    data:
        tier: Legendary
        jobtype: archmagetc
        level: 270
        artifact_level: 40
        passive_skill_level: 0
        combat_orders_level: 1
environment:
    use_doping: true
    armor: 300
    mob_level: 265
    force_advantage: 1
    v_skill_level: 30
    hexa_skill_level: 1
    hexa_mastery_level: 1
    v_improvements_level: 60
    hexa_improvements_level: 0
    weapon_attack_power: 0
    passive_skill_level: 0
    combat_orders_level: 1
    weapon_pure_attack_power: 0
    jobtype: archmagetc
    level: 270
    character:
        stat:
            STR: 1105
            LUK: 2650
            INT: 5003
            DEX: 1030
            STR_multiplier: 90
            LUK_multiplier: 90
            INT_multiplier: 7009  # original value was 709
            DEX_multiplier: 90
            STR_static: 620
            LUK_static: 760
            INT_static: 16790
            DEX_static: 490
            attack_power: 1835
            magic_attack: 2617.8
            attack_power_multiplier: 4
            magic_attack_multiplier: 103
            critical_rate: 103
            critical_damage: 123
            boss_damage_multiplier: 366
            damage_multiplier: 191.7
            final_damage_multiplier: 40
            ignored_defence: 97.04813171494295
            MHP: 36030
            MMP: 24835
            MHP_multiplier: 5
            MMP_multiplier: 5
            elemental_resistance: 15
        action_stat:
            cooltime_reduce: 0
            summon_duration: 10
            buff_duration: 195
            cooltime_reduce_rate: 0
---
ELAPSE 10.0
ELAPSE 10.0
ELAPSE 10.0
ELAPSE 10.0
    """

    assert hasEnvironment(plan)


def test_provide_environment_augmented_plan():
    plan = """
author: "Alice"
provider:
    name: "BaselineEnvironmentProvider"
    data:
        tier: Legendary
        jobtype: archmagetc
        level: 270
        artifact_level: 40
        passive_skill_level: 0
        combat_orders_level: 1
---
ELAPSE 10.0
ELAPSE 10.0
    """

    augmented_plan = provideEnvironmentAugmentedPlan(plan)
    result = yaml.safe_load(augmented_plan.split("\n---")[0])

    SimulationEnvironment.model_validate(result["environment"])


def test_run_plan_raises_error_without_environment():
    plan = """
author: "Alice"
provider:
    name: "BaselineEnvironmentProvider"
    data:
        tier: Legendary
        jobtype: archmagetc
        level: 270
        artifact_level: 40
        passive_skill_level: 0
        combat_orders_level: 1
---
ELAPSE 10.0
ELAPSE 10.0
ELAPSE 10.0
ELAPSE 10.0  
"""
    with pytest.raises(ValueError):
        runPlan(plan)


def test_run_plan_runs_with_environment():
    plan = """
author: "Alice"
provider:
    name: "BaselineEnvironmentProvider"
    data:
        tier: Legendary
        jobtype: archmagetc
        level: 270
        artifact_level: 40
        passive_skill_level: 0
        combat_orders_level: 1
environment:
    use_doping: true
    armor: 300
    mob_level: 265
    force_advantage: 1
    v_skill_level: 30
    hexa_skill_level: 1
    hexa_mastery_level: 1
    v_improvements_level: 60
    hexa_improvements_level: 0
    weapon_attack_power: 0
    passive_skill_level: 0
    combat_orders_level: 1
    weapon_pure_attack_power: 0
    jobtype: archmagetc
    level: 270
    character:
        stat:
            STR: 1105
            LUK: 2650
            INT: 5003
            DEX: 1030
            STR_multiplier: 90
            LUK_multiplier: 90
            INT_multiplier: 7009  # original value was 709
            DEX_multiplier: 90
            STR_static: 620
            LUK_static: 760
            INT_static: 16790
            DEX_static: 490
            attack_power: 1835
            magic_attack: 2617.8
            attack_power_multiplier: 4
            magic_attack_multiplier: 103
            critical_rate: 103
            critical_damage: 123
            boss_damage_multiplier: 366
            damage_multiplier: 191.7
            final_damage_multiplier: 40
            ignored_defence: 97.04813171494295
            MHP: 36030
            MMP: 24835
            MHP_multiplier: 5
            MMP_multiplier: 5
            elemental_resistance: 15
        action_stat:
            cooltime_reduce: 0
            summon_duration: 10
            buff_duration: 195
            cooltime_reduce_rate: 0
---
ELAPSE 10.0
ELAPSE 10.0
ELAPSE 10.0
ELAPSE 10.0  
CAST "체인 라이트닝 VI"
"""
    result = runPlan(plan)
    assert len(result) > 0
