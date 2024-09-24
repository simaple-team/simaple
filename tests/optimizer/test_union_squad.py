import time

import pytest
from loguru import logger

from simaple.core import JobType, Stat
from simaple.core.damage import INTBasedDamageLogic
from simaple.data.system.union_block import create_with_some_large_blocks
from simaple.optimizer import StepwizeOptimizer, UnionSquadTarget


@pytest.mark.parametrize(
    "maximum_cost, expected_stat",
    [
        (
            5,
            {
                "critical_rate": 8.0,
                "critical_damage": 5.0,
                "ignored_defence": 5.0,
                "MMP_multiplier": 6.0,
            },
        ),
        (
            10,
            {
                "INT_static": 160.0,
                "attack_power": 20.0,
                "magic_attack": 20.0,
                "critical_rate": 8.0,
                "critical_damage": 5.0,
                "boss_damage_multiplier": 5.0,
                "damage_multiplier": 3.2,
                "ignored_defence": 5.0,
                "MMP_multiplier": 6.0,
            },
        ),
        (
            15,
            {
                "INT_static": 560.0,
                "attack_power": 20.0,
                "magic_attack": 20.0,
                "critical_rate": 8.0,
                "critical_damage": 5.0,
                "boss_damage_multiplier": 5.0,
                "damage_multiplier": 3.2,
                "ignored_defence": 5.0,
                "MMP_multiplier": 6.0,
            },
        ),
        (
            30,
            {
                "STR_static": 280.0,
                "LUK_static": 520.0,
                "INT_static": 640.0,
                "DEX_static": 200.0,
                "attack_power": 20.0,
                "magic_attack": 20.0,
                "critical_rate": 8.0,
                "critical_damage": 5.0,
                "boss_damage_multiplier": 5.0,
                "damage_multiplier": 3.2,
                "ignored_defence": 5.0,
                "MHP_multiplier": 5.0,
                "MMP_multiplier": 6.0,
            },
        ),
    ],
)
def test_optimizer(maximum_cost, expected_stat):
    initial_squad = create_with_some_large_blocks([JobType.archmagefb])
    optimization_target = UnionSquadTarget(
        Stat(
            INT=40000,
            LUK=5000,
            magic_attack=3000,
            critical_rate=80,
            critical_damage=100,
            damage_multiplier=300,
            ignored_defence=90,
            INT_static=10000,
        ),
        INTBasedDamageLogic(attack_range_constant=1.0, mastery=0.95),
        initial_squad,
        preempted_jobs=[JobType.archmagefb],
    )
    optimizer = StepwizeOptimizer(optimization_target, maximum_cost, 1)
    start = time.time()
    output = optimizer.optimize()
    elapsed = time.time() - start

    assert sum(output.state) == maximum_cost
    logger.info(f"Optimization output {str(output.state)}; size {sum(output.state)}; spent: {elapsed:.02f}s")

    assert initial_squad.get_masked(output.state).get_stat().short_dict() == expected_stat
