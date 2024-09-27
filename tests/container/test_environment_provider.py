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
            "도트 퍼니셔": 10,
        },
    )
    env = env.get_simulation_environment()
    assert env.skill_levels == {
        "도트 퍼니셔": 10,
        "포이즌 노바": 30,
        "오버로드 마나": 30,
        "포이즌 체인": 30,
        "퓨리 오브 이프리트": 30,
        "메이플월드 여신의 축복": 30,
        "인페르날 베놈": 1,
        "플레임 스윕 VI": 1,
        "미스트 이럽션 VI": 1,
        "플레임 헤이즈 VI": 1,
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
            "도트 퍼니셔": 10,
        },
    )
    env = env.get_simulation_environment()
    assert env.skill_levels == {
        "도트 퍼니셔": 10,
        "포이즌 노바": 30,
        "오버로드 마나": 30,
        "포이즌 체인": 30,
        "퓨리 오브 이프리트": 30,
        "메이플월드 여신의 축복": 30,
        "인페르날 베놈": 1,
        "플레임 스윕 VI": 1,
        "미스트 이럽션 VI": 1,
        "플레임 헤이즈 VI": 1,
    }
