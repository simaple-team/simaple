from simaple.optimizer import Iterator, HyperstatStepwizeOptimizationTarget, StepwizeOptimizer
import pytest
from simaple.job.job import Job
from simaple.core.base import BaseStatType, AttackType, Stat


@pytest.mark.parametrize("length, depth", [
    (7, 3),
    (8, 2),
    (9, 4),
    (6, 1),
])
def test_iterator(length, depth):
    iterator = Iterator()
    count = 0
    for tup in iterator.cumulated_iterator(length, depth):
        count += 1
