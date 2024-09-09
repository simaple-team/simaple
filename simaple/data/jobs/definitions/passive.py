from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field

from simaple.core import ActionStat, ExtendedStat, JobType, Stat
from simaple.data.patch import SkillLevelPatch
from simaple.spec.loadable import (  # pylint:disable=unused-import
    TaggedNamespacedABCMeta,
)
from simaple.spec.loader import SpecBasedLoader
from simaple.spec.patch import EvalPatch, Patch
from simaple.spec.repository import DirectorySpecRepository


class PassiveSkill(BaseModel, metaclass=TaggedNamespacedABCMeta("PassiveSkill")):
    """
    Passive is no-state no-change property of user-class.
    """

    stat: Stat = Field(default_factory=Stat)
    action_stat: ActionStat = Field(default_factory=ActionStat)
    name: str

    def get_extended_stat(self) -> ExtendedStat:
        return ExtendedStat(
            stat=self.stat.model_copy(), action_stat=self.action_stat.model_copy()
        )
