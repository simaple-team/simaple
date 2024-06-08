import pytest

from simaple.core import JobType, Stat
from simaple.core.damage import INTBasedDamageLogic
from simaple.data.system.link import get_kms_link_skill_set
from simaple.optimizer import LinkSkillTarget, StepwizeOptimizer


@pytest.mark.parametrize(
    "maximum_cost, expected_reward_value",
    [
        (3, 21985589.273639064),
        (6, 24803206.28323931),
        (12, 28930802.18317819),
        (13, 29456254.7869325),
    ],
)
def test_optimizer(maximum_cost: int, expected_reward_value: float):
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
        get_kms_link_skill_set(),
        preempted_jobs=[JobType.archmagefb],
    )
    optimizer = StepwizeOptimizer(optimization_target, maximum_cost, 1)
    output = optimizer.optimize()
    assert output.get_value() == pytest.approx(expected_reward_value)
