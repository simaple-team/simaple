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
from simaple.data.jobs.definitions import PassiveHyperskillInterface


from pathlib import Path
from typing import cast

from simaple.core.damage import DamageLogic
from simaple.core.jobtype import JobType
from simaple.data.passive.patch import SkillLevelPatch
from simaple.spec.loadable import TaggedNamespacedABCMeta  # noqa: F401
from simaple.spec.loader import SpecBasedLoader
from simaple.spec.patch import EvalPatch
from simaple.spec.repository import DirectorySpecRepository





def get_skill_profile(jobtype: JobType) -> SkillProfile:
    repository = DirectorySpecRepository(str(Path(__file__).parent / "resources"))
    loader = SpecBasedLoader(repository)
    return cast(
        SkillProfile,
        loader.load(
            query={"group": jobtype.value, "kind": "SkillProfile"},
        ),
    )

def get_every_hyper_skills(group: str) -> list[PassiveHyperskillInterface]:
    repository = DirectorySpecRepository(str(Path(__file__).parent / "resources"))
    loader = SpecBasedLoader(repository)
    return loader.load_all(
        query={"group": group, "kind": "PassiveHyperskill"},
    )


def get_damage_logic(jobtype: JobType, combat_orders_level: int) -> DamageLogic:
    repository = DirectorySpecRepository(str(Path(__file__).parent))
    loader = SpecBasedLoader(repository)
    patches = [
        SkillLevelPatch(
            combat_orders_level=combat_orders_level,
            passive_skill_level=0,
        ),
        EvalPatch(injected_values={}),
    ]
    return cast(
        DamageLogic,
        loader.load(
            query={"group": jobtype.value, "kind": "DamageLogic"},
            patches=patches,
        ),
    )
