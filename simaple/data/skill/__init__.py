"""
Data Monsterlife
labeling rule
level:
  - normal: availabla to most user and most time
  - strong: available to few people
  - specific: available at specific period
"""

from pathlib import Path

from simaple.spec.loader import SpecBasedLoader
from simaple.spec.repository import DirectorySpecRepository


def get_kms_skill_loader() -> SpecBasedLoader:
    repository = DirectorySpecRepository(
        str(Path(__file__).parent / "resources" / "components")
    )
    return SpecBasedLoader(repository)
