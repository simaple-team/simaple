import json
import os
import pathlib
from abc import abstractmethod
from pathlib import Path
from typing import cast

import pydantic

from simaple.core import Stat
from simaple.core.damage import (
    DamageLogic,
    DEXBasedDamageLogic,
    INTBasedDamageLogic,
    LUKBasedDamageLogic,
    STRBasedDamageLogic,
)
from simaple.core.jobtype import JobType
from simaple.data.passive.patch import SkillLevelPatch
from simaple.spec.loadable import (  # pylint:disable=unused-import
    TaggedNamespacedABCMeta,
)
from simaple.spec.loader import SpecBasedLoader
from simaple.spec.patch import EvalPatch, Patch
from simaple.spec.repository import DirectorySpecRepository


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
