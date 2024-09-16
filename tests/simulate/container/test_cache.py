import json
from abc import ABC, abstractmethod

from simaple.container.cache import LocalstorageCache
from simaple.container.character_provider import BaselineSimulationConfig
from simaple.container.simulation import (
    CharacterDependentSimulationConfig,
    CharacterProvidingConfig,
    SimulationSetting,
)
from simaple.core import ExtendedStat, JobType
from simaple.core.job_category import JobCategory


def test_cache():
    saved_cache = {}
    cache = LocalstorageCache(saved_cache)

    setting = SimulationSetting()
    character_provider = BaselineSimulationConfig(
        union_block_count=10,
        tier="Legendary",
        jobtype=JobType.archmagefb,
        job_category=JobCategory.magician,
        level=270,
        passive_skill_level=0,
        combat_orders_level=1,
        artifact_level=40,
    )
    second_character_provider = BaselineSimulationConfig(
        union_block_count=10 + 1,
        tier="Legendary",
        jobtype=JobType.archmagefb,
        job_category=JobCategory.magician,
        level=270,
        passive_skill_level=0,
        combat_orders_level=1,
        artifact_level=40,
    )

    (extend_stat, config), hit = cache.get(setting, character_provider)
    assert not hit

    (extend_stat, config), hit = cache.get(setting, character_provider)
    assert hit

    (extend_stat, config), hit = cache.get(setting, second_character_provider)
    assert not hit

    exported_cache = cache.export()
    new_cache = LocalstorageCache(exported_cache)
    (extend_stat, config), hit = new_cache.get(setting, character_provider)
    assert hit

    (extend_stat, config), hit = cache.get(setting, second_character_provider)
    assert hit
