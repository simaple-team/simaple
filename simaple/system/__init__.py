import pydantic

from simaple.core import ActionStat, ExtendedStat, Stat
from simaple.spec.loadable import (  # pylint:disable=unused-import
    TaggedNamespacedABCMeta,
)


class NamedStat(
    pydantic.BaseModel, metaclass=TaggedNamespacedABCMeta(kind="NamedStat")
):
    name: str
    stat: Stat = pydantic.Field(default_factory=Stat)
    action_stat: ActionStat = pydantic.Field(default_factory=ActionStat)

    def get_extended_stat(self) -> ExtendedStat:
        return ExtendedStat(
            stat=self.stat.copy(),
            action_stat=self.action_stat.copy(),
        )

    def get_name(self) -> str:
        return self.name


class Doping(NamedStat):
    ...


class MonsterlifeMob(NamedStat):
    ...
