import time

import pytest
from loguru import logger

from simaple.core import AttackType, BaseStatType, Stat
from simaple.core.damage import INTBasedDamageLogic
from simaple.optimizer import StepwizeOptimizer, UnionOccupationTarget
from simaple.union import UnionOccupationStat


@pytest.mark.parametrize("maximum_cost", [20, 40, 60])
def test_optimizer(maximum_cost):
    optimization_target = UnionOccupationTarget(
        Stat(
            INT=40000,
            LUK=5000,
            magic_attack=3000,
            critical_rate=80,
            critical_damage=100,
            damage_multiplier=300,
            ignored_defence=90,
        ),
        INTBasedDamageLogic(attack_range_constant=1.0, mastery=0.95),
        UnionOccupationStat(),
    )
    optimizer = StepwizeOptimizer(optimization_target, maximum_cost, 2)
    start = time.time()
    output = optimizer.optimize()
    elapsed = time.time() - start
    logger.info(f"Optimization output {str(output.state)}; spent: {elapsed:.02f}s")
