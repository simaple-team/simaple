from pathlib import Path
from typing import cast

from simaple.spec.loadable import TaggedNamespacedABCMeta  # noqa: F401
from simaple.spec.loader import SpecBasedLoader
from simaple.spec.repository import DirectorySpecRepository
from simaple.system.artifact import ArtifactEffect


def get_artifact_effects() -> list[ArtifactEffect]:
    repository = DirectorySpecRepository(str(Path(__file__).parent))
    loader = SpecBasedLoader(repository)
    return cast(
        list[ArtifactEffect],
        loader.load_all(),
    )
