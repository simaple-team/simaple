from pathlib import Path
from typing import cast

import pydantic

from simaple.core import JobType
from simaple.spec.loadable import (  # pylint:disable=unused-import
    TaggedNamespacedABCMeta,
)
from simaple.spec.loader import SpecBasedLoader
from simaple.spec.repository import DirectorySpecRepository
from simaple.data.jobs.definitions.skill_profile import SkillProfile





def get_skill_profile(jobtype: JobType) -> SkillProfile:
    repository = DirectorySpecRepository(str(Path(__file__).parent / "resources"))
    loader = SpecBasedLoader(repository)
    return cast(
        SkillProfile,
        loader.load(
            query={"group": jobtype.value, "kind": "SkillProfile"},
        ),
    )
