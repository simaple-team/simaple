from pathlib import Path

from simaple.spec.loader import SpecBasedLoader
from simaple.spec.repository import DirectorySpecRepository
from simaple.system.hexa_stat import HexaStatCoreType


def get_all_hexa_stat_cores() -> list[HexaStatCoreType]:
    repository = DirectorySpecRepository(str(Path(__file__).parent))
    loader = SpecBasedLoader(repository)

    hexa_stat_cores: list[HexaStatCoreType] = loader.load_all(
        query={"kind": "HexaStatCoreType"},
    )
    return hexa_stat_cores
