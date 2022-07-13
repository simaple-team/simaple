from abc import ABCMeta, abstractmethod
from typing import List, Literal

from pydantic import BaseModel

from simaple.core import Stat
from simaple.gear.gear import Gear
from simaple.gear.gear_type import GearType
from simaple.gear.improvements.base import GearImprovement


class GearImprovementCalculator(BaseModel, metaclass=ABCMeta):
    @abstractmethod
    def compute(self, stat: Stat, gear: Gear) -> GearImprovement:
        ...


class Scroll(BaseModel):
    type: Literal["Scroll"]
    stat: Stat
    name: str
    gear_types: List[GearType]
