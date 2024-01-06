from pathlib import Path

from simaple.data.passive_hyper_skill.spec import PassiveHyperskillInterface
from simaple.spec.loader import SpecBasedLoader
from simaple.spec.repository import DirectorySpecRepository


def get_every_hyper_skills(group: str) -> list[PassiveHyperskillInterface]:
    repository = DirectorySpecRepository(str(Path(__file__).parent / "resources"))
    loader = SpecBasedLoader(repository)
    return loader.load_all(
        query={"group": group, "kind": "PassiveHyperskill"},
    )
