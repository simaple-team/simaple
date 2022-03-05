from typing import List, Literal

from pydantic import BaseModel

from simaple.core.base import Stat
from simaple.gear.gear import Gear
from simaple.gear.gear_type import GearType


class Scroll(BaseModel):
    type: Literal["Scroll"]
    stat: Stat
    name: str
    gear_types: List[GearType]

    def calculate_improvement(self, gear: Gear) -> Stat:
        if not self.is_gear_acceptable(gear):
            raise TypeError("Given gear type is not available to use this scroll")

        return self.stat.copy()

    def is_gear_acceptable(self, gear: Gear) -> bool:
        return gear.type in self.gear_types
