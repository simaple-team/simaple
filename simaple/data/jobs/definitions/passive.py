from pydantic import BaseModel, Field

from simaple.core import ActionStat, ExtendedStat, Stat
from simaple.spec.loadable import (  # pylint:disable=unused-import
    TaggedNamespacedABCMeta,
)


class PassiveSkill(BaseModel, metaclass=TaggedNamespacedABCMeta("PassiveSkill")):
    """
    Passive is no-state no-change property of user-class.
    """

    stat: Stat = Field(default_factory=Stat)
    action_stat: ActionStat = Field(default_factory=ActionStat)
    name: str

    def get_extended_stat(self) -> ExtendedStat:
        return ExtendedStat(stat=self.stat.model_copy(), action_stat=self.action_stat.model_copy())
