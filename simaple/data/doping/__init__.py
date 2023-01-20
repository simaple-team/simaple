"""
Data Doping
labeling rule
level: doping level.
  - normal: availabla to most user and most time
  - strong: available to few people
  - specific: available at specific period
"""

import os
from pathlib import Path

from simaple.core import ExtendedStat, Stat
from simaple.spec.loader import SpecBasedLoader
from simaple.spec.repository import DirectorySpecRepository
from simaple.system import Doping, NamedStat


def get_doping_loader() -> SpecBasedLoader:
    repository = DirectorySpecRepository(str(Path(__file__).parent))
    return SpecBasedLoader(repository)


def get_normal_doping() -> ExtendedStat:
    loader = get_doping_loader()

    dopings: list[NamedStat] = loader.load_all(
        query={"kind": "NamedStat", "level": "normal"}
    )

    return sum((doping.get_extended_stat() for doping in dopings), ExtendedStat())
