from simaple.container.environment_provider import (
    BaselineEnvironmentProvider,
    MinimalEnvironmentProvider,
)
from simaple.core import ActionStat, JobType, Stat


def test_minimal_environment_provider_passes_skill_levels():
    env = MinimalEnvironmentProvider(
        stat=Stat(),
        action_stat=ActionStat(),
        combat_orders_level=0,
        weapon_pure_attack_power=0,
        jobtype=JobType.archmagefb,
        level=280,
        hexa_skill_levels={
            "undef 인페르날 베놈": 10,
        },
    )
    env = env.get_simulation_environment()
    assert env.hexa_skill_levels == {
        "undef 인페르날 베놈": 10,
    }


def test_baseline_environment_provider_passes_skill_levels():
    env = BaselineEnvironmentProvider(
        tier="Legendary",
        jobtype=JobType.archmagefb,
        level=270,
        passive_skill_level=0,
        combat_orders_level=1,
        artifact_level=1,
        v_skill_level=30,
        v_improvements_level=60,
        hexa_improvements_level=10,
        hexa_skill_levels={
            "undef 인페르날 베놈": 10,
        },
    )
    env = env.get_simulation_environment()
    assert env.hexa_skill_levels == {
        "undef 인페르날 베놈": 10,
    }
