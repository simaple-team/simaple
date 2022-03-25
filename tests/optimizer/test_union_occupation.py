import time

import pytest
from loguru import logger

from simaple.core import AttackType, BaseStatType, Stat
from simaple.job.job import Job
from simaple.optimizer import StepwizeOptimizer, UnionOccupationTarget


class TestJob(Job):
    attack_range_constant: float = 1.0
    mastery: float = 0.95

    def get_base_stat_factor(self, stat: Stat) -> float:
        return stat.get_base_stat_coefficient(
            BaseStatType.INT
        ) * 4 + stat.get_base_stat_coefficient(BaseStatType.LUK)

    def get_attack_type_factor(self, stat: Stat) -> float:
        return stat.get_attack_coefficient(AttackType.magic_attack)


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
        TestJob(),
    )
    optimizer = StepwizeOptimizer(optimization_target, maximum_cost, 2)
    start = time.time()
    output = optimizer.optimize()
    elapsed = time.time() - start
    logger.info(f"Optimization output {str(output.state)}; spent: {elapsed:.02f}s")
