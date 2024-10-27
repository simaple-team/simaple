import pytest

import simaple.simulate.component.common  # noqa: F401
import simaple.simulate.component.specific  # noqa: F401
from simaple.core import ActionStat, Stat
from simaple.data.jobs.builtin import build_skills
from simaple.simulate.core.runtime import SimulationRuntime
from simaple.simulate.kms import get_builder


@pytest.fixture
def archmagefb_simulation_runtime() -> SimulationRuntime:
    skill_components = build_skills(
        [
            "archmagefb",
            "common",
            "int_based",
            "magician",
            "adventurer",
            "adventurer.int",
            "adventurer.magician",
            "mob",
        ],
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
        {},
        {},
        {
            "character_level": 260,
            "character_stat": Stat(),
            "combat_orders_level": 0,
            "passive_skill_level": 0,
            "weapon_pure_attack_power": 0,
            "weapon_attack_power": 0,
        },
    )
    return get_builder(skill_components, ActionStat()).build_simulation_runtime()
