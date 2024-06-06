import time

import pytest
from loguru import logger

from simaple.core import Stat
from simaple.core.damage import INTBasedDamageLogic
from simaple.optimizer import HyperstatTarget, StepwizeOptimizer
from simaple.system.hyperstat import get_kms_hyperstat


@pytest.mark.parametrize(
    "maximum_cost, expected_state",
    [
        (50, [0, 0, 0, 0, 1, 3, 2, 3, 3, 5]),
        (300, [0, 1, 1, 0, 2, 7, 5, 8, 6, 8]),
        (1200, [0, 3, 2, 0, 4, 12, 10, 12, 10, 13]),
    ],
)
def test_optimizer(maximum_cost: int, expected_state: list[int]):
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
        get_kms_hyperstat(),
    )
    optimizer = StepwizeOptimizer(optimization_target, maximum_cost, 1)
    start = time.time()
    output = optimizer.optimize()
    elapsed = time.time() - start
    logger.info(f"Optimization output {str(output.state)}; spent: {elapsed:.02f}s")
    assert output.state == expected_state
