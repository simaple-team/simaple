"""
Data Monsterlife
labeling rule
level:
  - normal: availabla to most user and most time
  - strong: available to few people
  - specific: available at specific period
"""

import os
from pathlib import Path

from simaple.core import ExtendedStat, Stat
from simaple.spec.loader import SpecBasedLoader
from simaple.spec.repository import DirectorySpecRepository
from simaple.system import MonsterlifeMob, NamedStat


def get_monsterlife_loader() -> SpecBasedLoader:
    repository = DirectorySpecRepository(str(Path(__file__).parent))
    return SpecBasedLoader(repository)


def get_normal_monsterlife() -> ExtendedStat:
    loader = get_monsterlife_loader()

    monster_life_mobs: list[NamedStat] = loader.load_all(
        query={"kind": "NamedStat", "level": "normal"}
    )

    return sum((mob.get_extended_stat() for mob in monster_life_mobs), ExtendedStat())
