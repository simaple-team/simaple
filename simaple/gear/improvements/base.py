from abc import ABCMeta, abstractmethod
from typing import List, Literal, Optional

from pydantic import BaseModel

from simaple.core import Stat
from simaple.gear.gear import GearMeta
from simaple.gear.gear_type import GearType


class GearImprovement(BaseModel, metaclass=ABCMeta):
    type: str

    @abstractmethod
    def calculate_improvement(
        self, meta: GearMeta, ref_stat: Optional[Stat] = None
    ) -> Stat:
        ...


class Scroll(BaseModel):
    type: Literal["Scroll"]
    stat: Stat
    name: str
    gear_types: List[GearType]
