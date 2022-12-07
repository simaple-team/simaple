import copy
from abc import abstractmethod

import pydantic

from simaple.core import Stat
from simaple.spec.loadable import (  # pylint:disable=unused-import
    TaggedNamespacedABCMeta,
)


class PassiveHyperskillInterface(
    pydantic.BaseModel, metaclass=TaggedNamespacedABCMeta(kind="PassiveHyperskill")
):
    @abstractmethod
    def get_target_name(self) -> str:
        ...

    @abstractmethod
    def modify(self, origin: dict) -> dict:
        ...

    @abstractmethod
    def get_name(self) -> str:
        ...


class PassiveHyperskill(PassiveHyperskillInterface):
    target: str
    name: str

    def get_target_name(self) -> str:
        return self.target

    def get_name(self) -> str:
        return self.name


class ValueIncreasePassiveHyperskill(PassiveHyperskill):
    key: str
    increment: float

    def modify(self, origin: dict) -> dict:
        modified = copy.deepcopy(origin)
        modified[self.key] += self.increment

        return modified


class MultiplierPassiveHyperskill(PassiveHyperskill):
    key: str
    multiplier: float

    def modify(self, origin: dict) -> dict:
        modified = copy.deepcopy(origin)
        modified[self.key] *= self.multiplier

        return modified


class StatIncreasePassiveHyperskill(PassiveHyperskill):
    key: str
    increment: Stat

    def modify(self, origin: dict) -> dict:
        original_stat = Stat.parse_obj(origin.get(self.key, Stat()))
        modified_stat = original_stat + self.increment

        modified = copy.deepcopy(origin)
        modified[self.key] = modified_stat.short_dict()

        return modified
