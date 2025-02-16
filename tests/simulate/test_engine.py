import os

import pytest

import simaple.simulate.component.common  # noqa: F401
from simaple.container.environment_provider import BaselineEnvironmentProvider
from simaple.container.memoizer import PersistentStorageMemoizer
from simaple.container.usecase.builtin import get_engine
from simaple.core.jobtype import JobType
from simaple.simulate.engine import NoOpError
from simaple.simulate.policy.parser import parse_simaple_runtime


def test_run_engine():
    _environment_provider = BaselineEnvironmentProvider(
        tier="Legendary",
        jobtype=JobType.archmagefb,
        level=270,
        passive_skill_level=0,
        combat_orders_level=1,
        artifact_level=40,
        v_skill_level=30,
        v_improvements_level=60,
        hexa_improvements_level=10,
    )
    _simulation_environment_memoizer = PersistentStorageMemoizer(
        os.path.join(os.path.dirname(__file__), ".memo.simaple.json")
    )
    environment = _simulation_environment_memoizer.compute_environment(
        _environment_provider
    )
    engine = get_engine(environment)
    _, commands = parse_simaple_runtime(
        """
author: "Alice"
provider:
    name: "BaselineEnvironmentProvider"
    data:
        tier: Legendary
        jobtype: archmagetc
        job_category: 1 # mage
        level: 270
        artifact_level: 40
        passive_skill_level: 0
        combat_orders_level: 1
---
CAST "오버로드 마나"
CAST "이프리트 VI"
CAST "메디테이션"
CAST "파이어 오라 VI"
CAST "인피니티"
ELAPSE 78000

CAST "메이플월드 여신의 축복"

# CAST "포이즌 리전"
CAST "플레임 헤이즈 VI"

CAST "에픽 어드벤쳐"
CAST "소울 컨트랙트"
CAST "리스트레인트 링"
CAST "메기도 플레임 VI"
CAST "인페르날 베놈"
CAST "퓨리 오브 이프리트"
CAST "포이즌 노바"
CAST "도트 퍼니셔"
CAST "포이즌 체인"
CAST "미스트 이럽션 VI"
CAST "플레임 헤이즈 VI"
CAST "크레스트 오브 더 솔라"
CAST "플레임 스윕 VI"
CAST "플레임 스윕 VI"
!debug "list(filter(has_cooldown, filter(available, viewer('validity'))))"

CAST "메테오"

CAST "미스트 이럽션 VI"
CAST "플레임 헤이즈 VI"
x4 CAST "플레임 스윕 VI"

CAST "미스트 이럽션 VI"
CAST "플레임 헤이즈 VI"
x4 CAST "플레임 스윕 VI"

CAST "미스트 이럽션 VI"
CAST "플레임 헤이즈 VI"
x4 CAST "플레임 스윕 VI"

!debug "list(filter(has_cooldown, filter(available, viewer('validity'))))"
"""
    )

    for command in commands:
        engine.exec(command)

    text_outputs = []
    for operation_log in engine.operation_logs():
        if operation_log.description is not None:
            text_outputs.append(operation_log.description)

    assert len(text_outputs) == 2


def test_run_engine_reject_no_op():
    _environment_provider = BaselineEnvironmentProvider(
        tier="Legendary",
        jobtype=JobType.archmagefb,
        level=270,
        passive_skill_level=0,
        combat_orders_level=1,
        artifact_level=40,
        v_skill_level=30,
        v_improvements_level=60,
        hexa_improvements_level=10,
    )
    _simulation_environment_memoizer = PersistentStorageMemoizer(
        os.path.join(os.path.dirname(__file__), ".memo.simaple.json")
    )
    environment = _simulation_environment_memoizer.compute_environment(
        _environment_provider
    )
    engine = get_engine(environment)
    _, commands = parse_simaple_runtime(
        """
author: "Alice"
provider:
    name: "BaselineEnvironmentProvider"
    data:
        tier: Legendary
        jobtype: archmagetc
        job_category: 1 # mage
        level: 270
        artifact_level: 40
        passive_skill_level: 0
        combat_orders_level: 1
---
CAST "오버로드 마나"
CAST "이프리트"
CAST "없는 스킬"
"""
    )

    with pytest.raises(NoOpError):
        for command in commands:
            engine.exec(command)
