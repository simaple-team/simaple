import pydantic

from simaple.core import Stat
from simaple.spec.loadable import (  # pylint:disable=unused-import
    TaggedNamespacedABCMeta,
)


class NamedStat(
    pydantic.BaseModel, metaclass=TaggedNamespacedABCMeta(kind="NamedStat")
):
    name: str
    stat: Stat

    def get_stat(self) -> Stat:
        return self.stat.copy()

    def get_name(self) -> str:
        return self.name


class Doping(NamedStat):
    ...


class MonsterlifeMob(NamedStat):
    ...
