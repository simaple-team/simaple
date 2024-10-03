import pytest

from simaple.container.simulation import (
    FinalCharacterStat,
    SimulationEnvironment,
    get_operation_engine,
    get_skill_components,
)
from simaple.core import ActionStat, JobType, Stat
from simaple.simulate.policy.base import Operation


def test_simulation_environment_using_skill_levels():
    # Test case 1: Verify the simulation environment with default skill levels
    no_skill_environment = SimulationEnvironment(
        passive_skill_level=0,
        combat_orders_level=0,
        weapon_pure_attack_power=0,
        jobtype=JobType.archmagefb,
        level=280,
        character=FinalCharacterStat(
            stat=Stat(
                INT=1000,
                magic_attack=1000,
            ),
            action_stat=ActionStat(),
            active_buffs={},
        ),
        v_improvements_level=60,
    )

    environment_with_skill_level = SimulationEnvironment(
        passive_skill_level=0,
        combat_orders_level=0,
        weapon_pure_attack_power=0,
        jobtype=JobType.archmagefb,
        level=280,
        character=FinalCharacterStat(
            stat=Stat(
                INT=1000,
                magic_attack=1000,
            ),
            action_stat=ActionStat(),
            active_buffs={},
        ),
        v_improvements_level=60,
        skill_levels={
            "인페르날 베놈": 10,
        },
    )

    engine = get_operation_engine(no_skill_environment)
    engine_with_skill = get_operation_engine(environment_with_skill_level)

    op = Operation(
        command="CAST",
        name="인페르날 베놈",
        expr="",
    )

    assert engine.exec(op) != engine_with_skill.exec(op)
