import time

import pytest
from loguru import logger

from simaple.core import AttackType, BaseStatType, JobType, Stat
from simaple.core.damage import INTBasedDamageLogic
from simaple.link import LinkSkillset
from simaple.optimizer import LinkSkillTarget, StepwizeOptimizer


@pytest.mark.parametrize("maximum_cost", [3, 6, 12, 13])
def test_optimizer(maximum_cost):
    optimization_target = LinkSkillTarget(
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
        LinkSkillset.KMS(),
        preempted_jobs=[JobType.archmagefb],
    )
    optimizer = StepwizeOptimizer(optimization_target, maximum_cost, 1)
    start = time.time()
    output = optimizer.optimize()
    elapsed = time.time() - start
    logger.info(
        f"Optimization output {str(output.state)}; size {sum(output.state)}; spent: {elapsed:.02f}s"
    )
