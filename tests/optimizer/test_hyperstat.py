import time

import pytest
from loguru import logger

from simaple.core import AttackType, BaseStatType, Stat
from simaple.core.damage import INTBasedDamageLogic
from simaple.hyperstat import Hyperstat
from simaple.optimizer import HyperstatTarget, StepwizeOptimizer


@pytest.mark.parametrize("maximum_cost", [50, 300])
def test_optimizer(maximum_cost):
    optimization_target = HyperstatTarget(
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
        Hyperstat.KMS(),
    )
    optimizer = StepwizeOptimizer(optimization_target, maximum_cost, 1)
    start = time.time()
    output = optimizer.optimize()
    elapsed = time.time() - start
    logger.info(f"Optimization output {str(output.state)}; spent: {elapsed:.02f}s")
