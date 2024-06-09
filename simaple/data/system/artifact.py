from __future__ import annotations

from pathlib import Path

from simaple.spec.loader import SpecBasedLoader
from simaple.spec.repository import DirectorySpecRepository
from simaple.system.artifact import Artifact, ArtifactEffect
from simaple.system.optimal_artifact import get_optimal_artifact_generator


def get_artifact_effects() -> list[ArtifactEffect]:
    repository = DirectorySpecRepository(str(Path(__file__).parent))
    loader = SpecBasedLoader(repository)

    return loader.load_all(
        query={"kind": "ArtifactEffect"},
    )


def get_artifact(card_priorities: list[str], artifact_level: int) -> Artifact:
    generator = get_optimal_artifact_generator()

    return Artifact(
        cards=generator.get_optimal_artifact(artifact_level, card_priorities),
        effects=get_artifact_effects(),
    )
