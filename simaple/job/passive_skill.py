from pydantic import BaseModel, Field

from simaple.core import ActionStat, Stat
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


class DefaultActiveSkill(
    BaseModel, metaclass=TaggedNamespacedABCMeta("DefaultActiveSkill")
):
    """
    Passive is no-state no-change property of user-class.
    """

    stat: Stat = Field(default_factory=Stat)
    action_stat: ActionStat = Field(default_factory=ActionStat)
    name: str
