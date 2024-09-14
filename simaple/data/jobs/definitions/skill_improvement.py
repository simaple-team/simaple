import copy
from abc import abstractmethod

import pydantic

from simaple.core import Stat
from simaple.spec.loadable import (  # pylint:disable=unused-import
    TaggedNamespacedABCMeta,
)
from simaple.spec.patch import Patch


class SkillImprovement(
    pydantic.BaseModel, metaclass=TaggedNamespacedABCMeta(kind="SkillImprovement")
):
    @abstractmethod
    def get_target_names(self) -> list[str]: ...

    @abstractmethod
    def modify(self, origin: dict) -> dict: ...


class _Advantage(pydantic.BaseModel):
    target_name: str
    target_field: str
    value: int


class SkillAdditiveImprovement(SkillImprovement):
    name: str
    advantages: list[_Advantage]

    def get_target_names(self) -> list[str]:
        return [v.target_name for v in self.advantages]

    def _get_target_advantages(self, target_name: str) -> list[_Advantage]:
        return [v for v in self.advantages if v.target_name in target_name]

    def modify(self, origin: dict) -> dict:
        advantages = self._get_target_advantages(origin["name"])
        if len(advantages) == 0:
            return origin

        modified = copy.deepcopy(origin)

        for advantage in advantages:
            assert (
                advantage.target_field in origin
            ), "Fields may defined in target, but missing"
            modified[advantage.target_field] += advantage.value

        return modified
