import pytest

import simaple.simulate.component.skill  # noqa: F401
import simaple.simulate.component.specific  # noqa: F401
from simaple.core.base import ActionStat
from simaple.simulate.engine import MonotonicEngine
from simaple.simulate.kms import get_builder


@pytest.fixture
def archmagefb_engine() -> MonotonicEngine:
    return get_builder(
        ["archmagefb", "common", "adventurer.magician", "mob"],
        {
            "도트 퍼니셔": 30,
            "포이즌 노바": 30,
            "오버로드 마나": 30,
            "포이즌 체인": 30,
            "퓨리 오브 이프리트": 30,
        },
        {
            "플레임 스윕": 60,
            "미스트 이럽션": 60,
            "플레임 헤이즈": 60,
            "메기도 플레임": 60,
            "이그나이트": 60,
            "파이어 오라": 60,
            "이프리트": 60,
        },
        {"character_level": 260, "action_stat": ActionStat()},
    ).build_monotonic_engine()
