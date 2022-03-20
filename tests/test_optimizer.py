from simaple.optimizer import Iterator, HyperstatStepwizeOptimizationTarget, StepwizeOptimizer
import pytest
from simaple.job.job import Job
from simaple.core.base import BaseStatType, AttackType, Stat
import time
from loguru import logger

class TestJob(Job):
    attack_range_constant: float = 1.0
    mastery: float = 0.95

    def get_base_stat_factor(self, stat: Stat) -> float:
        return stat.get_base_stat_coefficient(BaseStatType.INT) * 4 + stat.get_base_stat_coefficient(BaseStatType.LUK)

    def get_attack_type_factor(self, stat: Stat) -> float:
        return stat.get_base_stat_coefficient(AttackType.magic_attack)


def test_optimizer():
    optimization_target = HyperstatStepwizeOptimizationTarget(
        Stat(INT=40000, LUK=5000, magic_attack=3000, critical_rate=80, critical_damage=100, damage_multiplier=300, ignored_defence=90),
        TestJob()
    )
    for maximum_cost in [300, 1200]: 
        optimizer = StepwizeOptimizer(
            optimization_target, maximum_cost, 1
        )
        start = time.time()
        output = optimizer.optimize()
        elapsed = time.time() - start
        logger.info(f"Optimization output {str(output.state)}; spent: {elapsed:.02f}s")
