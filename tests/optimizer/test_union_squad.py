import time

import pytest
from loguru import logger

from simaple.core import JobType, Stat
from simaple.core.damage import INTBasedDamageLogic
from simaple.optimizer import StepwizeOptimizer, UnionSquadTarget
from simaple.union import UnionSquad


@pytest.mark.parametrize("maximum_cost", [5, 10, 15, 30])
def test_optimizer(maximum_cost):
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
        UnionSquad.create_with_some_large_blocks([JobType.archmagefb]),
        preempted_jobs=[JobType.archmagefb],
    )
    optimizer = StepwizeOptimizer(optimization_target, maximum_cost, 1)
    start = time.time()
    output = optimizer.optimize()
    elapsed = time.time() - start

    assert sum(output.state) == maximum_cost
    logger.info(
        f"Optimization output {str(output.state)}; size {sum(output.state)}; spent: {elapsed:.02f}s"
    )
