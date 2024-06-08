from pydantic import BaseModel

from simaple.core.base import ExtendedStat
from simaple.spec.loadable import (  # pylint:disable=unused-import
    TaggedNamespacedABCMeta,
)


class UpgradableUserStat(
    BaseModel, metaclass=TaggedNamespacedABCMeta(kind="UpgradableUserStat")
):
    name: str
    values: list[ExtendedStat]

    def get_extended_stat(self, level: int) -> ExtendedStat:
        return self.values[level].model_copy(deep=True)

    def get_name(self) -> str:
        return self.name
