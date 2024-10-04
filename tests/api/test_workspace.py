import pytest
import yaml

from simaple.api.base import (
    compute_maximum_dealing_interval,
    get_initial_plan_from_baseline,
    has_environment,
    provide_environment_augmented_plan,
    run_plan,
    run_plan_with_hint,
)
from simaple.container.environment_provider import BaselineEnvironmentProvider
from simaple.container.simulation import SimulationEnvironment
from simaple.core import JobType


@pytest.fixture
def fixture_environment_given_plan() -> str:
    return """
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
    v_improvements_level: 60
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
ELAPSE 30000.0
ELAPSE 10.0
ELAPSE 10.0
ELAPSE 10.0
ELAPSE 10.0
CAST "체인 라이트닝 VI"
!debug "seq(viewer('validity')).filter(available).filter(has_cooldown).to_list()"
ELAPSE 30000.0
"""


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

    assert not has_environment(plan)


def test_retreives_skill_level_with_unicode():
    plan = """
author: "Alice"
provider:
    name: "BaselineEnvironmentProvider"
    data:
        tier: Legendary
        jobtype: archmagefb
        level: 270
        artifact_level: 40
        passive_skill_level: 0
        combat_orders_level: 1
        hexa_improvements_levels:
          도트 퍼니셔: 3
---
ELAPSE 10.0
ELAPSE 10.0
ELAPSE 10.0
ELAPSE 10.0
    """

    new_plan = provide_environment_augmented_plan(plan)
    assert "도트 퍼니셔" in new_plan


def test_has_environment_returns_true_with_environment(fixture_environment_given_plan):
    assert has_environment(fixture_environment_given_plan)


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

    augmented_plan = provide_environment_augmented_plan(plan)
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
    with pytest.raises(Exception):
        run_plan(plan)


def test_run_plan_runs_with_environment(fixture_environment_given_plan):
    result = run_plan(fixture_environment_given_plan)

    assert len(result) > 0


def test_compute_maximum_dealing_interval(fixture_environment_given_plan):
    result = compute_maximum_dealing_interval(fixture_environment_given_plan, 30000)
    assert result.damage > 0


def test_get_initial_plan_from_baseline():
    given_environment = BaselineEnvironmentProvider(
        tier="Legendary",
        jobtype=JobType("archmagetc"),
        level=270,
        artifact_level=0,
        passive_skill_level=0,
        combat_orders_level=1,
    )

    output = get_initial_plan_from_baseline(given_environment)
    assert output.find("CAST")
    assert not has_environment(output)


@pytest.mark.parametrize(
    "given, change",
    [
        (
            """CAST "체인 라이트닝 VI"
x10 ELAPSE 10000
ELAPSE 10000
""",
            """ELAPSE 12345
x10 CAST "체인 라이트닝 VI"
CAST "체인 라이트닝 VI"
ELAPSE 10000
ELAPSE 10000
ELAPSE 10000
""",
        ),
        (
            """CAST "체인 라이트닝 VI"
x10 ELAPSE 10000
ELAPSE 10000
""",
            """CAST "체인 라이트닝 VI"
x10 ELAPSE 10000
ELAPSE 10000
ELAPSE 10000
ELAPSE 10000
ELAPSE 10000
""",
        ),
    ],
)
def test_run_with_hint(fixture_environment_given_plan, given, change):
    previous_plan = f"""
{fixture_environment_given_plan}
{given}"""
    new_plan = f"""
{fixture_environment_given_plan}
{change}
"""

    first_result = run_plan(previous_plan)
    second_result = run_plan(new_plan)

    second_result_with_hint = run_plan_with_hint(
        previous_plan,
        first_result,
        new_plan,
    )

    assert len(second_result_with_hint) == len(second_result)
    assert second_result_with_hint == second_result
